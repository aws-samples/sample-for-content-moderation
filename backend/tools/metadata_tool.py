import json
import os
from config import METADATA_RESOURCE_PATH


def save_metadata(metadata_key:str, json_info:dict):
    if not os.path.exists(METADATA_RESOURCE_PATH):
        os.makedirs(METADATA_RESOURCE_PATH)

    context_file = os.path.join(METADATA_RESOURCE_PATH,f'{metadata_key}.json')
    if not os.path.exists(context_file):
        with open(context_file, 'w') as f:
            json.dump(json_info, f)

def load_metadata(metadata_key: str) -> dict:
    context_file = os.path.join(METADATA_RESOURCE_PATH, f'{metadata_key}.json')
    if os.path.exists(context_file):
        with open(context_file, 'r') as f:
            return json.load(f)
    else:
        # 如果文件不存在，可以返回空字典或抛出异常，根据需求选择
        return {}


# if __name__ == '__main__':
#     # save_metadata("haha", {
#     #     "sadf":"sdfs"
#     # })
#
#     print(load_metadata("haha"))