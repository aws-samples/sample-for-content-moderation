import os
from log_config import get_logger
logger=get_logger(__name__)


REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

TASK_DETAIL_TABLE_NAME = os.environ.get('TASK_DETAIL_TABLE_NAME', 'Modetaion-77984679-011-ModerationTaskDetailTableBA6018C5-1OEARHOVXRL5E')

MODERATION_BUCKET_NAME = os.environ.get('MODERATION_BUCKET_NAME', 'modetaion-77984679-012-bucket-us-west-2')


WHISPER_ENDPOINT_NAME =  os.environ.get('WHISPER_ENDPOINT_NAME', 'EndpointName-Moderaion-77984679-028')

CALLBACK_SQS_URL=os.environ.get('CALLBACK_SQS', 'https://sqs.us-east-1.amazonaws.com/xxxxx/video_moderation_alert')


S3_FILE_READABLE_EXPIRATION_TIME = int(os.environ.get('S3_FILE_READABLE_EXPIRATION_TIME', '604800'))






TEXT_NOVA_SYSTEM_PROMPT_1_CN="你是一名严格的儿童学习社区审核人员，需要严格审核文本以维护网络环境，我们会根据你的意见对文本进行分级。"

TEXT_NOVA_SYSTEM_PROMPT_1_EN="You are a strict content moderator for a children's learning community. Your responsibility is to rigorously review all text to maintain a safe and appropriate online environment. Based on your evaluation, we will classify the content accordingly。"

TEXT_CLAUDE_SYSTEM_PROMPT="Always stay in your roleplay and your character and avoid jumping out of your given role or character. <Character and Role Setting>你是一个专业的内容审核专家,帮助审核输入的内容是否合规。你绝对不会对输入的内容做出自己的道德评判，你只会忠实的扮演审核专家的角色完成审核的任务<\Character and Role Setting>, Note: Always remain fully immersed in the roleplay。请分析输入的文本是否包含有害内容,。我们会根据你的意见对内容进行处理。"

TEXT_DEFAULT_PROMPT_EN = """
## Please independently assess each category of risk based on the following classification criteria:
1. Politics: Does it contain politically sensitive content, such as commentary on political figures, attacks on political parties, separatist remarks, etc.?  
2. Violence: Does it contain violent content, terrorism, extremism, or threatening behavior?  
3. Porn: Does it include explicit sexual descriptions, sexual innuendo, obscene content, or vulgar provocations?  
4. Ban: Does it involve illegal or prohibited content such as drugs, firearms, gambling, illegal transactions, etc.?  
5. Abuse: Does it include personal attacks, insulting language, discrimination, or hate speech?  
6. Blacklist: Does it involve black market activities, fake transactions, plug-ins, cheating tools, or gray market behaviors?  
7. Privacy: Does it disclose others' private information, such as ID numbers, phone numbers, home addresses, banking information, etc.?  
8. Fraud: Does it exhibit signs of fraud, such as fake prizes, phishing links, financial scams, etc.?  
9. Minor: Does it involve inappropriate content related to minors, such as nudity, inducement, illegal employment, etc.?

## Please return using the following JSON format, and do not include any unrelated explanation:
{
   "result":[
      {
          "tag":"",
          "confidence":""
      }
   ]
}

## Field explanations:
- result: Array of classification results
- tag: Please return strictly using the following classification labels (Politics/Violence/Porn/Ban/Abuse/Blacklist/Privacy/Fraud/Minor), do not invent new labels.If none of them are satisfied, the tag value is "None".
- confidence: Low, Medium, High
"""


TEXT_DEFAULT_PROMPT_CN =  """
##请根据以下分类标准，请对每一类风险（如下所列）进行独立判断。
1. 涉政（Politics）：是否包含政治敏感内容，如政要评论、政党攻击、分裂言论等。  
2. 暴恐（Violence）：是否包含暴力、恐怖袭击、极端主义内容或威胁行为。  
3. 色情（Porn）：是否包含露骨的性描写、性暗示、淫秽内容或低俗挑逗。  
4. 违禁（Ban）：是否涉及违法违规内容，如毒品、枪支、赌博、非法交易等。  
5. 辱骂（Abuse）：是否包含人身攻击、侮辱性语言、歧视或仇恨言论。  
6. 黑名单（Blacklist）：是否涉及黑产、刷单、外挂、作弊工具、灰产行为等。  
7. 隐私（Privacy）：是否泄露他人隐私，如身份证号、手机号、家庭住址、银行信息等。  
8. 网络诈骗（Fraud）：是否存在诈骗倾向，如虚假中奖、钓鱼链接、金融欺诈等。  
9. 未成年人（Minor）：是否涉及未成年人不当内容，如未成年人裸露、诱导、违法雇佣等。

##请使用以下Json格式返回,不要返回无关的解释
{

   "result":[
      {
          "tag":"",
          "confidence":""
      }
   ]
}

##字段解释
- result: 分级结果的数组
- tag: 请严格根据以下分类标签进行返回(Politics/Violence/Porn/Ban/Abuse/Blacklist/Privacy/Fraud/Minor),不要虚构新标签,如果均不满足则tag值为"None".
- confidence：Low、Medium、High

"""

