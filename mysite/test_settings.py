import os

os.environ.setdefault(
    'SUPPORTBOT_LINE_CHANNEL_SECRET',
    os.environ.get('SUPPORTBOT_TEST_LINE_CHANNEL_SECRET', 'test-line-secret'),
)

from .settings import *
