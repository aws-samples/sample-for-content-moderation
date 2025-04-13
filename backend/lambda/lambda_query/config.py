import os

USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')
TASK_DETAIL_TABLE_NAME = os.environ.get('TASK_DETAIL_TABLE_NAME', 'task_detail_moderation')
REGION_NAME = os.environ.get('REGION_NAME', 'us-east-1')

TASK_ID_QUERY_INDEX = os.environ.get('TASK_ID_QUERY_INDEX', 'TaskIdQueryIndex')
TASK_ID_QUERY_INDEX_KEY_NAME = os.environ.get('TASK_ID_QUERY_INDEX_KEY_NAME', 'task_id_query')

