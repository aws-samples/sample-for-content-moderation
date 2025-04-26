import os

USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')
TASK_DETAIL_TABLE_NAME = os.environ.get('TASK_DETAIL_TABLE_NAME', 'Moderaion-77984679-032-ModerationTaskDetailTableBA6018C5-TA3XRHH31IWL')
REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

TASK_ID_QUERY_INDEX = os.environ.get('TASK_ID_QUERY_INDEX', 'TaskIdQueryIndex')
TASK_ID_QUERY_INDEX_KEY_NAME = os.environ.get('TASK_ID_QUERY_INDEX_KEY_NAME', 'task_id_query')

