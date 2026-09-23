from django.test import TestCase
from django.urls import reverse

from supportbot.models import InquiryLog


class SupportBotWebhookTests(TestCase):
    def test_line_webhook_auto_reply_for_known_question(self):
        response = self.client.post(
            reverse('line-webhook'),
            data={
                'events': [
                    {
                        'source': {'userId': 'U123'},
                        'message': {'text': '料金を教えてください'},
                    }
                ]
            },
            content_type='application/json',
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

    def test_index_describes_available_endpoints(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['title'], 'AI・チャットボット自動連携システム（POC）')
        self.assertEqual(payload['endpoints']['line'], '/api/inquiries/line/')
