import os
from tools.log_config import get_logger
logger=get_logger(__name__)


REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

CLUSTER_NAME = os.environ.get('CLUSTER_NAME', 'vm_cluster')

TASK_DEFINITION_ARN = os.environ.get('TASK_DEFINITION_ARN', 'arn:aws:ecs:us-east-1:xxxxx:task-definition/contentmoderation_3:11')

SUBNET_IDS = os.environ.get('SUBNET_IDS', 'subnet-02a8e392bba3ce0a2,subnet-07c91d052b99a704c')

CONTAINER_NAME = os.environ.get('CONTAINER_NAME', 'cm3')


#程序类型 0:持续处理SQS消息   1:仅尝试处理1条SQS  2:持续处理SQS消息，直到监听x次消息队列后后没有消息响应
# Program types:
# 0: Continuously process SQS messages
# 1: Attempt to process only 1 SQS message
# 2: Continuously process SQS messages until no response after listening to the queue x times
PROGRAM_TYPE = int(os.environ.get('PROGRAM_TYPE', 2))

#SQS重试次数，直到尝试监听x次消息队列后后没有消息响应
# SQS retry count, until no response after attempting to listen to the message queue x times
ATTEMPT_COUNT = int(os.environ.get('ATTEMPT_COUNT', 2))



BATCH_PROCESS_IMG_NUMBER = int(os.environ.get('BATCH_PROCESS_IMG_NUMBER', 3))


logger.info(f"The environment variable is {PROGRAM_TYPE}")
logger.info(f"The number of message attempts is {ATTEMPT_COUNT}")


USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')


TASK_DETAIL_TABLE_NAME = os.environ.get('TASK_DETAIL_TABLE_NAME', 'task_detail_moderation')

TASK_TABLE_NAME = os.environ.get('TASK_TABLE_NAME', 'task_moderation')

MODERATION_BUCKET_NAME = os.environ.get('MODERATION_BUCKET_NAME', 'video-moderation-a')

S3_FILE_READABLE_EXPIRATION_TIME = int(os.environ.get('S3_FILE_READABLE_EXPIRATION_TIME', '604800'))


S3BUCKET_CUSTOMER_DIR = os.environ.get('S3BUCKET_CUSTOMER_DIR', 'customer_video')

# IMAGE_CDN_PATH = os.environ.get('IMAGE_CDN_PATH', 'https://d14tamu6in7iln.cloudfront.net')


ROOT_RESOURCE_PATH= "ffmpeg_output"

FACE_RESOURCE_PATH="face"

MODEL_ID = os.environ.get('MODEL_ID', "us.amazon.nova-micro-v1:0")
IMG_MODEL_ID = os.environ.get('IMG_MODEL_ID', "us.amazon.nova-lite-v1:0")


logger.info(f"Text Model id is {MODEL_ID}")
logger.info(f"Image Model id is {IMG_MODEL_ID}")



#VISUAL_MODERATION_TYPE :  video  / image
#video only supports nove model
VISUAL_MODERATION_TYPE = os.environ.get('VISUAL_MODERATION_TYPE', "video")

logger.info(f"VISUAL_MODERATION_TYPE is {VISUAL_MODERATION_TYPE}")



WHISPER_ENDPOINT_NAME =  os.environ.get('WHISPER_ENDPOINT_NAME', 'content-moderation-endpoint-whisper')


MODERATION_SQS_URL= os.environ.get('MODERATION_SQS', 'https://sqs.us-east-1.amazonaws.com/xxxxx/video_moderation')

S3_MODERATION_SQS= os.environ.get('S3_MODERATION_SQS', 'https://sqs.us-east-1.amazonaws.com/xxxxx/s3_video_moderation')

CALLBACK_SQS_URL=os.environ.get('CALLBACK_SQS', 'https://sqs.us-east-1.amazonaws.com/xxxxx/video_moderation_alert')



# 首次建立连接 最大重连次数
# Maximum reconnect attempts for the first time establishing the connection
START_CONNECT_MAX_RETRIES = 10

# 直播结束后/意外断流 最大重连次数
# Maximum reconnect attempts after the live stream ends / unexpected disconnection
END_CONNECT_MAX_RETRIES = 5

# 重连尝试间隔x秒
# Reconnect attempt interval in x seconds
RETRY_DELAY = 1

# 每个audio片段的持续时间（秒）
# The duration (in seconds) of each audio segment
AUDIO_SEGMENT_DURATION = 10

# 图片截取频率
# Image capture frequency
SNAPSHOT_INTERVAL = 1

SPLIT_VIDEO_INTERVAL = 10


SPEECH_RECOGNIZER_PLUGIN = os.environ.get('SPEECH_RECOGNIZER_PLUGIN', 'sagemaker')
TEXT_MODERATION_PLUGIN = os.environ.get('TEXT_MODERATION_PLUGIN', 'bedrock')
#IMAGE_MODERATION_PLUGIN :   bedrock or rekognition
IMAGE_MODERATION_PLUGIN = os.environ.get('IMAGE_MODERATION_PLUGIN', 'bedrock')

logger.info(f"TEXT_MODERATION_PLUGIN is {TEXT_MODERATION_PLUGIN}")

logger.info(f"IMAGE_MODERATION_PLUGIN is {IMAGE_MODERATION_PLUGIN}")

SYSTEM_0325_NOVA_VIDEO_CN = '''您是网络社区的严格内容管理员。您的职责是仔细、严格地审核每个视频，以维护安全健康的网络环境。为了保护读者免受不当内容的侵害，每个视频必须单独审核，并且每个视频应根据指南至少审核两次。请单独分析每个视频，并判断其是否符合审核标准。您的判断将用于视频评级。'''
SYSTEM_0325_NOVA_VIDEO_EN = '''You are a strict content moderator for the online community. Your job is to carefully and rigorously review each video to maintain a safe and healthy online environment. To protect readers from inappropriate content, each video must be reviewed individually, and each video should be reviewed at least twice according to the guidelines. Please analyze each video individually and judge whether it complies with the review criteria. Your judgment will be used to rate the video.'''

VIDEO_PROMPT_0325_CN = '''
## 请根据以下审核标准进行审核,每个视频可能违反多条规则。
 1. HighlySensitiveBehavior
 - 性行为，包括描绘实际或模拟的性行为（如人类性交、口交等，涉及身体部位对生殖器的刺激），也包括身体液体（如精液或阴道液体）的描绘，以及涉及束缚、纪律、统治、屈服及施虐受虐狂的情节。涉及性玩具（用于性刺激或愉悦的物体或设备，如假阳具、振动器、肛塞、节拍等）。
 - 涉及裸露，包括裸露的男性下体生殖器和疑似物（无论是勃起还是松弛、阴囊和任何可辨别的阴毛）、裸露的女性生殖器（女性生殖系统，包括外阴、阴道和任何可观察到的阴毛）、裸露的臀部或肛门（人类的臀部或肛门，包括臀部裸体或通过透明衣物可辨别臀部的情况，特别适用于可以直接看到臀部或肛门的情境，而非任何内衣或衣服可以完全或部分覆盖的情况）、裸露的女性乳头（人类女性乳头，包括完全可见或部分可见的乳头及乳头周围的区域）。
 - 男性手淫及疑似手淫的行为（手握生殖器/睪丸/阴茎/龟头/棍状物等似物品、裸露阴茎、用手对下体进行触摸、用手对裆部进行触摸、手捏阴茎）、女性手淫、对敏感性器官进行裸露。
 - 疑似男性生殖器的裸露物(肉棒/阴茎/棍状物/Penis/Testicles/Genitalia/Dick)、男性撒尿。
 - 涉及私密部位和非露骨裸体，包括非露骨裸体（裸露的背部、背部大部分皮肤可见的情况）、裸露的男性乳头、臀部部分暴露〔由于衣物过短导致部分裸露的臀部〕、女性乳房部分暴露〔乳房内侧褶皱、乳头被遮挡、下乳房折痕可见〕、女性乳沟裸露、女性胸部部分露出。
 - 隐含的裸体〔裸体情境但臀部、乳头或生殖器等私密部位被遮掩或无法完全看见〕。私密部位遮挡（女性乳头被不透明衣物或遮掩物遮住但形状清晰可见）、男性生殖器遮挡〔男性生殖器或阴茎被不透明衣物或遮掩物遮住但形状清晰可见〕,
 - 亲吻嘴唇
2. Behavior2
 - 着装暴露，穿以下暴露身体的服饰(游泳衣、游泳裤、胸罩、内裤)
3. SuspectedSensitiveBehavior
 - 其它疑似行为(视频中只有一只手指、视频中只有一只手、视频中有一只手并且下面有很多毛发、视频中是一个模糊的手、视频中手放在裤裆位置摸一根手指、视频中一只手指指向一个肿块、视频中一只手指和一个有伤口的肿块)。
 - 如果视频中只有一只手指/只有一只手/只有一只手并且下面有很多毛发/只是一个模糊的手/手放在裤裆位置摸一根手指/一只手指指向一个肿块/手指和一个有伤口的肿块/模糊的手指。  
4. Politics
 - 涉及政治人物、政党、国家领导人等评论
 - 有分裂言论、政治攻击、涉政标语等
5. Violence
 - 暴力行为、血腥画面、打斗、尸体、枪击
 - 恐怖袭击、极端主义旗帜或标志、武装冲突
6. Ban
 - 枪支、刀具、毒品、赌博、非法交易场景等
 - 涉及违法交易、暗网、诈骗类视觉提示
7. Alcohol
 - 展示酒精饮料（瓶、杯装酒等）
 - 饮酒行为、聚会饮酒场景
8. Blurry
 - 视频过于模糊确认或其它原因无法确认
9. OtherSensitiveBehavior
- 除上述中提及的分类外，其余疑似不适合儿童观看的影像内容。


## 请用json格式输出，请确保格式的正确，请不要输出无关的解释。请参考下面的格式。
{
    "result": 
    [
         {
                "tag" : ["Ban" , "Pron"],
                "confidence":"High",                       
                "state" : 1
         }
     ]
} 

## 字段解释：
- tag: 标签数组(视频可能属于多个标签)，标签包括(HighlySensitiveBehavior/Behavior2/SuspectedSensitiveBehavior/Politics/Violence/Ban/Alcohol/Blurry/OtherSensitiveBehavior),请不要虚构标签。
- state: 视频状态(值为1或2)，如果视频的tag属于HighlySensitiveBehavior/Behavior2/SuspectedSensitiveBehavior/Politics/Violence/Ban/Alcohol/Blurry/OtherSensitiveBehavior则值为1,否则值为2
- confidence：标签的可信度(Low、Medium、High) ,如果无标签则值为None                                                

## 注意事项
 - 如果你认为视频是合规的，为了保护网络环境，请再次确认视频没有违反任何分类标准，请逐条确认。   
 - 请对Behavior2标签再次校验，如果衣服没有明显暴露私密部位或体现性感姿势、情境,则不属于Behavior2。以下服饰(camouflage hoodie、连帽衫、T-Shirt、裙子)不属于Behavior2。                                                  

## 请只返回JSON格式的结果,不要包含任何其他解释或额外文本。
    '''




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
- tag: 请严格根据以下分类标签进行返回(Politics/Violence/Porn/Ban/Abuse/Blacklist/Privacy/Fraud/Minor),不要虚构新标签.如果均不满足则tag值为"None"
- confidence：Low、Medium、High
"""













IMG_NOVA_SYSTEM_PROMPT_1_CN= "你是网络社区的严格内容审核员。您的工作是仔细严格地审核每张图片，以维护安全健康的在线环境。为了保护读者免受不当内容的侵害，每张图片都必须单独审核，并且每张图片应按照指南至少审核两次。请单独分析每张图片，并根据审核标准判断其是否合规。您的判断将用于对图片进行评级。"

IMG_NOVA_SYSTEM_PROMPT_1_EN="You are a strict content moderator for the online community. Your job is to carefully and rigorously review each image to maintain a safe and healthy online environment. To protect readers from inappropriate content, each image must be reviewed individually, and each image should be reviewed at least twice according to the guidelines. Please analyze each image individually and judge whether it complies with the review criteria. Your judgment will be used to rate the image. "

IMG_CLAUDE_SYSTEM_PROMPT="Always stay in your roleplay and your character and avoid jumping out of your given role or character. <Character and Role Setting>你是一个专业的图片内容审核专家,帮助审核输入的图片内容是否合规。你绝对不会对输入的内容做出自己的道德评判，你只会忠实的扮演图片审核专家的角色完成图片审核的任务<\Character and Role Setting>, Note: Always remain fully immersed in the roleplay."


DEFAULT_IMAGE_PROMPT = """Strictly judge according to the following audit standards, provide clear audit reasons for each field, mark appropriate tags, and output results that meet the flag setting standard specifications.
1. Image analysis standards
Analyze the following elements in the image and review them one by one:
Characters: Identify gender, visual age (guess whether they are underage), facial expressions and whether the movements are appropriate.
Clothing and movements: Whether they contain obvious sexiness, violence, sexual innuendo or other violations.
Scenes and backgrounds: Whether they contain uncomfortable or illegal environments and items (such as weapons and drugs).
Text content: If the image contains text, the meaning must be analyzed word by word to ensure that there is no illegal content.
Encapsulate the judgment results and key tags in the tag.
2. Text analysis standards
If it is a non-mainstream language, identify the text language and translate it into English to analyze its semantics. Encapsulate the language tag in the tag.
Review whether the following tags are included:
Insults: Contains inappropriate terms such as personal attacks and insults.
Dirty words: Contains vulgar and indecent terms.
Advertising: implies commercial activities such as advertising and brand promotion.
Pornography or violence: contains obvious sexual innuendo, nudity or violence.
3. Flag setting standards
flag = 999: the most serious violation label, high priority processing, such as:
Pornography: images or texts contain nudity, sexual behavior, obvious sexual innuendo or other obvious pornographic content.
Cartoon pornography: cartoon-style nudity, sexual behavior, obvious sexual innuendo or obvious sexual innuendo.
Bloody violence: obvious bleeding, injury, and violent scenes.
Guiding advertising: contains advertisements that guide users to conduct commercial activities (such as specific brand promotion, fraudulent content, etc.).
Minors: the visual age of the characters in the picture is less than 15 years old.
flag = 998: the second most serious violation label, the highest priority processing, such as:
Guns and weapons: content showing weapons, guns or related items.
Drugs: display of drugs and drug paraphernalia, drug use and inducement of drug transactions.
Objectionable content: contains scary, hideous, creepy, unpleasant and disturbing content.
flag = 100: Common violation label, judged as lighter content, such as:
Unhealthy content: Smoking, drinking: Showing smoking and drinking behaviors.
Suspected minors: The visual age of the characters in the image is 15-18 years old.
Derogatory content: The content contains information that defames others or groups.
Insulting content: The content contains personal attacks or insulting words.
Dirty words: The text or image contains vulgar and indecent words.
flag = 200: Suspected minors (15-18 years old).
flag = 0: No violation or no processing label.
flag = 1: No processing label, such as:
Sexy action: Non-pornographic but sexy action or clothing.
Sexy selfie: Non-pornographic but sexy selfie or clothing.
Cartoon minors: Non-pornographic cartoon minors.
flag = 2: The content is completely unrecognizable.
flag = 50: The image contains non-pornographic sexy actions or selfies.
4. Input and output examples
Input: {"name":"","bio":"",pic:[{"pid":1}]}
Output: {"name":{"flag":1,"reason":"","tag":[""]},"bio":{"flag":0,"reason":"","tag":[""]},"pic":[{"pid":1,"flag":1,"reason":"","tag":[""]}]}

Please return only the results in JSON format, without any other explanation or extra text.
"""




IMG_PROMPT_0325_CN = '''
 ## 请根据以下审核标准进行审核,每个图片可能违反多条规则。
 1. HighlySensitiveBehavior
 - 性行为，包括描绘实际或模拟的性行为（如人类性交、口交等，涉及身体部位对生殖器的刺激），也包括身体液体（如精液或阴道液体）的描绘，以及涉及束缚、纪律、统治、屈服及施虐受虐狂的情节。涉及性玩具（用于性刺激或愉悦的物体或设备，如假阳具、振动器、肛塞、节拍等）。
 - 涉及裸露，包括裸露的男性下体生殖器和疑似物（无论是勃起还是松弛、阴囊和任何可辨别的阴毛）、裸露的女性生殖器（女性生殖系统，包括外阴、阴道和任何可观察到的阴毛）、裸露的臀部或肛门（人类的臀部或肛门，包括臀部裸体或通过透明衣物可辨别臀部的情况，特别适用于可以直接看到臀部或肛门的情境，而非任何内衣或衣服可以完全或部分覆盖的情况）、裸露的女性乳头（人类女性乳头，包括完全可见或部分可见的乳头及乳头周围的区域）。
 - 男性手淫及疑似手淫的行为（手握生殖器/睪丸/阴茎/龟头/棍状物等似物品、裸露阴茎、用手对下体进行触摸、用手对裆部进行触摸、手捏阴茎）、女性手淫、对敏感性器官进行裸露。
 - 疑似男性生殖器的裸露物(肉棒/阴茎/棍状物/Penis/Testicles/Genitalia/Dick)、男性撒尿。
 - 涉及私密部位和非露骨裸体，包括非露骨裸体（裸露的背部、背部大部分皮肤可见的情况）、裸露的男性乳头、臀部部分暴露〔由于衣物过短导致部分裸露的臀部〕、女性乳房部分暴露〔乳房内侧褶皱、乳头被遮挡、下乳房折痕可见〕、女性乳沟裸露、女性胸部部分露出。
 - 隐含的裸体〔裸体情境但臀部、乳头或生殖器等私密部位被遮掩或无法完全看见〕。私密部位遮挡（女性乳头被不透明衣物或遮掩物遮住但形状清晰可见）、男性生殖器遮挡〔男性生殖器或阴茎被不透明衣物或遮掩物遮住但形状清晰可见〕,
 - 亲吻嘴唇
2. Behavior2
 - 着装暴露，穿以下暴露身体的服饰(游泳衣、游泳裤、胸罩、内裤)
3. SuspectedSensitiveBehavior
 - 其它疑似行为(图中只有一只手指、图中只有一只手、图中有一只手并且下面有很多毛发、图中是一个模糊的手、图中手放在裤裆位置摸一根手指、图中一只手指指向一个肿块、图中一只手指和一个有伤口的肿块)。
 - 如果图中只有一只手指/只有一只手/只有一只手并且下面有很多毛发/只是一个模糊的手/手放在裤裆位置摸一根手指/一只手指指向一个肿块/手指和一个有伤口的肿块/模糊的手指。  
4. Politics
 - 涉及政治人物、政党、国家领导人等评论
 - 有分裂言论、政治攻击、涉政标语等
5. Violence
 - 暴力行为、血腥画面、打斗、尸体、枪击
 - 恐怖袭击、极端主义旗帜或标志、武装冲突
6. Ban
 - 枪支、刀具、毒品、赌博、非法交易场景等
 - 涉及违法交易、暗网、诈骗类视觉提示
7. Alcohol
 - 展示酒精饮料（瓶、杯装酒等）
 - 饮酒行为、聚会饮酒场景
8. Blurry
 - 图片过于模糊确认或其它原因无法确认
9. OtherSensitiveBehavior
- 除上述中提及的分类外，其余疑似不适合儿童观看的影像内容。

## 请用json格式输出，请确保格式的正确，请不要输出无关的解释。如果有多个图，请将各自的结果放到数组中。请参考下面的格式。
```json
{
    "result": [
        {
            "img_index" : 1,
            "tag" : ["Ban" , "Pron"],
            "confidence":"High",                       
            "state" : 1
        },
        {
            "img_index" : 2,
            "tag" : ["Porn", "Alcohol"],
            "confidence":"Medium",   
            "state" : 1
        }
    ]
} 
```

## 字段解释：
- img_index: 图片序号，请不要虚构序号
- tag: 标签数组(图片可能属于多个标签)，标签包括(HighlySensitiveBehavior/Behavior2/SuspectedSensitiveBehavior/Politics/Violence/Ban/Alcohol/Blurry/OtherSensitiveBehavior),请不要虚构标签。
- state: 图片状态(值为1或2)，如果图片的tag属于HighlySensitiveBehavior/Behavior2/SuspectedSensitiveBehavior/Politics/Violence/Ban/Alcohol/Blurry/OtherSensitiveBehavior则值为1,否则值为2
- confidence：标签的可信度(Low、Medium、High) ,如果无标签则值为None                                                

## 注意事项
 - 如果你认为图片是合规的，为了保护网络环境，请再次确认图片没有违反任何分类标准，请逐条确认。   
 - 请对Behavior2标签再次校验，如果衣服没有明显暴露私密部位或体现性感姿势、情境,则不属于Behavior2。以下服饰(camouflage hoodie、连帽衫、T-Shirt、裙子)不属于Behavior2。                                                  
 - 请基于图片本身进行审核，不要进行幻想。 

##请直接输出json数据，请确保格式的正确，请不要输出无关的解释。                                                                                                                                                                                     

'''
