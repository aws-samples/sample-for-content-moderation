import os

REGION_NAME = os.environ.get('REGION_NAME', 'us-east-1')

MODEL_ID = os.environ.get('MODEL_ID', "us.amazon.nova-lite-v1:0")
# MODEL_ID = os.environ.get('MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')



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

DEFAULT_IMAGE_PROMPT_CN = """严格按照以下审核标准进行严格判断，为每个字段提供明确的审核理由，标注合适的标签(tag)，输出符合flag设置标准规范的结果。
1. 图片分析标准
   分析图片中的以下要素，并逐一审核：
       人物：识别性别、视觉年龄 (推测是否未成年)、面部表情和动作是否得体。
       服饰与动作：是否含有明显性感、暴力、性暗示或其他违规行为。
       场景与背景：是否包含令人不适或违规的环境、物品 (如武器、毒品)。
       文字内容：如果图片中包含文字，需逐字分析含义，确保没有违规内容。
       将判定结果与关键标签封装于 tag 中。
2. 文本分析标准
   若为非主流语言，识别文字语言并翻译成英文，以便分析其语义。将语种标签封装于 tag 中。
   审核是否包含以下标签：
       侮辱性：带有人身攻击、辱骂等不当用语。
       脏话：包含粗俗、不雅的用语。
       广告性：暗示广告、品牌推广等商业行为。
       色情或暴力：包含显著性暗示、裸露或暴力内容。
3. flag 设置标准
    flag = 999：最严重违规标签，高优先级处理，如：
       色情：图像或文字包含裸露、性行为、显著性暗示或其他显著色情内容。
       卡通色情：卡通形式的裸露、性行为、显著性暗示或显著性暗示。
       血腥暴力：明显的流血、伤害、暴力场景。
       引导性广告：包含引导用户进行商业行为的广告（如特定品牌推广、欺诈内容等）。
       未成年：图片中人物视觉年龄小于 15 岁。
    flag = 998：次严重违规标签，最高优先级处理，如：
       枪支与武器：展示武器、枪支或相关物品的内容。
       毒品：毒品和吸毒工具展示、吸毒和诱导性毒品交易。
       反感内容：包含恐怖、狰狞、毛骨悚然、令人不悦、不安的内容。
    flag = 100：普通违规标签，判定较轻内容，如：
       不健康内容：抽烟、喝酒：展示吸烟、饮酒行为。
       疑似未成年：图像中人物视觉年龄为 15-18 岁。
       诋毁性内容：内容含有诋毁他人或群体的信息。
       侮辱内容：内容中带有人身攻击或侮辱性用语。
       脏话：文字或图像包含粗俗、不雅用语。
    flag = 200：疑似未成年 (15-18 岁)。
    flag = 0：未命中违规或不处理标签。
    flag = 1：不处理标签，如：
       性感动作：非色情但具有一定性感意味的动作或服装。
       性感自拍：非色情但具有一定性感意味的自拍或服装。
       卡通未成年人物：非色情的卡通未成年形象。
    flag = 2：内容完全不可辨识。
    flag = 50：图片包含非色情的性感动作或自拍。
4. 输入输出示例
   输入： {"name":"","bio":"",pic:[{"pid":1}]}
   输出： {"name":{"flag":1,"reason":"","tag":[""]},"bio":{"flag":0,"reason":"","tag":[""]},"pic":[{"pid":1,"flag":1,"reason":"","tag":[""]}]}

   请只返回JSON格式的结果,不要包含任何其他解释或额外文本。
"""