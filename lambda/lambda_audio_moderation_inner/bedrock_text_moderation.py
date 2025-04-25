from bedrock_text_tool import invoke_claude, invoke_nova
from config import TEXT_NOVA_SYSTEM_PROMPT_1_EN,TEXT_CLAUDE_SYSTEM_PROMPT

class BedrockTextModeration:
    def moderate(self, model_id:str,prompt: str, content: str) -> str:
        if "nova" in model_id:
            return invoke_nova(model_id, TEXT_NOVA_SYSTEM_PROMPT_1_EN, prompt, content)
        elif "claude" in model_id:
            return invoke_claude(model_id,TEXT_CLAUDE_SYSTEM_PROMPT, prompt, content)
        else:
            return "error"

