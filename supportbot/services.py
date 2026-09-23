from django.conf import settings


SYSTEM_INSTRUCTION = (
    'あなたは問い合わせ一次対応を行う Gemini 3.6-flash です。'
    'ナレッジベースを参照し、回答できない内容のみ有人サポートへエスカレーションします。'
)


def build_response(message, channel):
    normalized = (message or '').lower()

    for entry in getattr(settings, 'SUPPORTBOT_KNOWLEDGE_BASE', []):
        if any(keyword.lower() in normalized for keyword in entry['keywords']):
            return {
                'channel': channel,
                'model': 'gemini-3.6-flash',
                'system_instruction': SYSTEM_INSTRUCTION,
                'decision': 'auto_reply',
                'reply': {
                    'text': entry['answer'],
                    'format': 'text',
                },
                'knowledge_refs': [entry['source']],
                'escalation': {
                    'required': False,
                    'target': '',
                },
                'storage_targets': ['supabase', 'google_sheets', 'jira', 'looker_studio'],
            }

    return {
        'channel': channel,
        'model': 'gemini-3.6-flash',
        'system_instruction': SYSTEM_INSTRUCTION,
        'decision': 'escalation',
        'reply': {
            'text': 'お問い合わせありがとうございます。担当者が内容を確認し、順次ご連絡します。',
            'format': 'text',
        },
        'knowledge_refs': [],
        'escalation': {
            'required': True,
            'target': 'human_support',
        },
        'storage_targets': ['supabase', 'google_sheets', 'jira', 'looker_studio'],
    }
