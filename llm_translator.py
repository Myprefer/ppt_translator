# llm_translator.py

from openai import OpenAI
import os

class LLMTranslator:
    # 支持的模型列表
    SUPPORTED_MODELS = {
        "qwen-turbo": {
            "name": "Qwen-Turbo",
            "description": "速度快，成本低，适合大量文本翻译",
            "max_tokens": 4000,
            "cost": "低"
        },
        "qwen-plus": {
            "name": "Qwen-Plus", 
            "description": "平衡性能与成本，推荐选择",
            "max_tokens": 8000,
            "cost": "中"
        },
        "qwen-max": {
            "name": "Qwen-Max",
            "description": "最高质量，适合专业翻译",
            "max_tokens": 16000,
            "cost": "高"
        },
        "qwen-max-longcontext": {
            "name": "Qwen-Max-LongContext",
            "description": "超长上下文，适合大文档翻译",
            "max_tokens": 32000,
            "cost": "高"
        }
    }
    
    @classmethod
    def get_available_models(cls):
        """获取可用模型列表"""
        return cls.SUPPORTED_MODELS
    
    @classmethod
    def is_valid_model(cls, model_name):
        """检查模型是否有效"""
        return model_name in cls.SUPPORTED_MODELS
    
    def __init__(self, api_key=None, base_url=None, model="qwen-turbo"):
        self.api_key = api_key if api_key else 'os.getenv("QWEN_API_KEY")'
        self.base_url = base_url if base_url else os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # 验证模型
        if not self.is_valid_model(model):
            raise ValueError(f"不支持的模型: {model}. 支持的模型: {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model = model

        if not self.api_key:
            raise ValueError("Qwen API key not provided and QWEN_API_KEY environment variable not set.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def translate_text(self, text_to_translate, target_language="English", context_texts=None):
        messages = [
            {"role": "system", "content": f"You are a professional translation assistant. Translate the given text into {target_language}. Maintain the original meaning, tone, and style. Consider the provided context for better accuracy and coherence."}
        ]

        if context_texts:
            context_str = "\n".join([f"- {ctx}" for ctx in context_texts])
            messages.append({"role": "user", "content": f"Context for translation:\n{context_str}\n\nText to translate: {text_to_translate}"})
        else:
            messages.append({"role": "user", "content": f"Translate the following text into {target_language}: {text_to_translate}"})

        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7 # Adjust temperature for creativity vs. accuracy
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error during translation: {e}")
            return None

if __name__ == "__main__":
    # Example Usage:
    # Set your Qwen API key and base URL as environment variables or pass them directly
    # For testing, you might need to set these:
    # os.environ["QWEN_API_KEY"] = "YOUR_QWEN_API_KEY"
    # os.environ["QWEN_BASE_URL"] = "YOUR_QWEN_BASE_URL" # Usually https://dashscope.aliyuncs.com/compatible-mode/v1

    # Test with dummy API key if not set, but actual translation will fail without a valid one
    if "QWEN_API_KEY" not in os.environ:
        print("Warning: QWEN_API_KEY environment variable not set. Translation will likely fail.")
        # For local testing without a real key, you might mock the API call or provide a dummy key
        # For this example, we'll proceed, but expect an error if key is missing.

    translator = LLMTranslator()

    # Test case 1: Simple translation
    text1 = "Hello, how are you?"
    translated_text1 = translator.translate_text(text1, target_language="中文")
    print(f"Original: {text1}\nTranslated: {translated_text1}\n")

    # Test case 2: Translation with context
    text2 = "The bank is on the corner."
    context2 = ["I need to withdraw money.", "The river bank is very scenic."]
    translated_text2 = translator.translate_text(text2, target_language="中文", context_texts=context2)
    print(f"Original: {text2}\nContext: {context2}\nTranslated: {translated_text2}\n")

    text3 = "He has a strong will."
    context3 = ["The will was read to the family.", "She will go to the store."]
    translated_text3 = translator.translate_text(text3, target_language="中文", context_texts=context3)
    print(f"Original: {text3}\nContext: {context3}\nTranslated: {translated_text3}\n")


