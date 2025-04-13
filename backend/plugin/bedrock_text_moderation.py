from base.plugin_interface import TextModeration
from config import MODEL_ID,TEXT_NOVA_SYSTEM_PROMPT_1_EN,TEXT_CLAUDE_SYSTEM_PROMPT
from tools.bedrock_text_tool import invoke_claude, invoke_nova



class BedrockTextModeration(TextModeration):
    def moderate(self,prompt: str, content: str) -> any:
        if "nova" in MODEL_ID:
            return invoke_nova(MODEL_ID, TEXT_NOVA_SYSTEM_PROMPT_1_EN, prompt, content)
        elif "claude" in MODEL_ID:
            return invoke_claude(MODEL_ID,TEXT_CLAUDE_SYSTEM_PROMPT, prompt, content)
        else:
            return None
