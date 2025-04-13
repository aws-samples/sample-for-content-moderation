import os

REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')

USER_ID = os.environ.get('USER_ID', 'l')
TOKEN_ARN = os.environ.get('TOKEN_ARN', 't')
CALLBACK_URL = os.environ.get('CALLBACK_URL', 'url')
