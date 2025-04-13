"""
@File    : config.py
@Time    : 2025/3/1 21:42
@Author  : tedli
@Email   : tedli@amazon.com
@Description: 
    This file is for...
"""
import os

REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')
USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')
