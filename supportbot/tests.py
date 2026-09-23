import hmac
import json
from base64 import b64encode
from hashlib import sha256

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from supportbot.models import InquiryLog


class SupportBotWebhookTests(TestCase):
    def _line_signature(self, payload):
        if isinstance(payload, str):
            body = payload.encode('utf-8')
        else:
            body = json.dumps(payload).encode('utf-8')
        return b64encode(
            hmac.new(
                settings.SUPPORTBOT_LINE_CHANNEL_SECRET.encode('utf-8'),
                body,
                sha256,
            ).digest()
        ).decode('utf-8')

    def test_line_webhook_auto_reply_for_known_question(self):
        payload = {
            'events': [
                {
                    'source': {'userId': 'U123'},
                    'message': {'text': '料金を教えてください'},
                }
            ]
        }
        response = self.client.post(
            reverse('line-webhook'),
            data=payload,
            content_type='application/json',
            headers={'X-Line-Signature': self._line_signature(payload)},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['decision'], 'auto_reply')
        self.assertIn('従量課金', payload['reply']['text'])
        self.assertEqual(InquiryLog.objects.count(), 1)
        self.assertEqual(InquiryLog.objects.get().status, InquiryLog.Status.AUTO_REPLY)

    def test_webform_webhook_escalates_for_unknown_question(self):
        response = self.client.post(
            reverse('webform-webhook'),
            data={
                'name': '山田花子',
                'email': 'hanako@example.com',
                'message': '独自の契約条件にも対応できますか',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['decision'], 'escalation')
        self.assertEqual(payload['escalation']['target'], 'human_support')
        log = InquiryLog.objects.get()
        self.assertEqual(log.status, InquiryLog.Status.ESCALATION)
        self.assertEqual(log.contact, 'hanako@example.com')

    def test_webhooks_reject_invalid_json_payloads(self):
        invalid_line_payload = '{"events": ['
        line_response = self.client.post(
            reverse('line-webhook'),
            data=invalid_line_payload,
            content_type='application/json',
            headers={'X-Line-Signature': self._line_signature(invalid_line_payload)},
        )
        webform_response = self.client.post(
            reverse('webform-webhook'),
            data='{"message": ',
            content_type='application/json',
        )

        self.assertEqual(line_response.status_code, 400)
        self.assertEqual(line_response.json()['error'], 'Invalid JSON payload.')
        self.assertEqual(webform_response.status_code, 400)
        self.assertEqual(webform_response.json()['error'], 'Invalid JSON payload.')

    def test_line_webhook_rejects_invalid_signature(self):
        payload = {'events': []}
        response = self.client.post(
            reverse('line-webhook'),
            data=payload,
            content_type='application/json',
            headers={'X-Line-Signature': 'invalid'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'Invalid LINE signature.')

    def test_index_describes_available_endpoints(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['title'], 'AI・チャットボット自動連携システム（POC）')
        self.assertEqual(payload['endpoints']['line'], '/api/inquiries/line/')
