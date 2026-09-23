import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from supportbot.models import InquiryLog
from supportbot.services import build_response


@require_GET
def index(request):
    return JsonResponse(
        {
            'title': 'AI・チャットボット自動連携システム（POC）',
            'workflow': [
                'LINE / Webフォームから問い合わせを受信',
                'Gemini 3.6-flash 想定のナレッジ検索結果で回答可否を判定',
                '自動返信または有人サポートへのエスカレーションを返却',
                'Supabase / GSS / Jira / Looker Studio 連携用のログ情報を保持',
            ],
            'endpoints': {
                'line': '/api/inquiries/line/',
                'webform': '/api/inquiries/webform/',
            },
        }
    )


def _load_body(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode('utf-8'))


def _save_log(channel, contact, message, response_payload):
    return InquiryLog.objects.create(
        channel=channel,
        contact=contact,
        message=message,
        status=response_payload['decision'],
        generated_reply=response_payload['reply']['text'],
        matched_knowledge=', '.join(response_payload['knowledge_refs']),
        escalation_target=response_payload['escalation']['target'],
        metadata={
            'model': response_payload['model'],
            'storage_targets': response_payload['storage_targets'],
        },
    )


@csrf_exempt
@require_POST
def line_webhook(request):
    payload = _load_body(request)
    event = (payload.get('events') or [{}])[0]
    message = event.get('message', {}).get('text', '')
    contact = event.get('source', {}).get('userId', '')
    response_payload = build_response(message=message, channel=InquiryLog.Channel.LINE)
    log = _save_log(InquiryLog.Channel.LINE, contact, message, response_payload)
    response_payload['log_id'] = log.id
    return JsonResponse(response_payload)


@csrf_exempt
@require_POST
def webform_webhook(request):
    payload = _load_body(request)
    message = payload.get('message', '')
    contact = payload.get('email') or payload.get('name', '')
    response_payload = build_response(message=message, channel=InquiryLog.Channel.WEBFORM)
    log = _save_log(InquiryLog.Channel.WEBFORM, contact, message, response_payload)
    response_payload['log_id'] = log.id
    return JsonResponse(response_payload)
