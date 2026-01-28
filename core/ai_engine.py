import requests
import io
from openai import OpenAI

class InterviewAI:
    def __init__(self, api_key, base_url="https://openrouter.ai/api/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.lemonfox_key = api_key # 假设你用同一个 key 或者在 UI 另设输入框

    def transcribe(self, audio_bytes, api_key):
        """调用 Lemonfox 将录音转换为文字"""
        url = "https://api.lemonfox.ai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # 将 Streamlit 的 bytes 转换为文件对象
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"language": "chinese"} # 设置为中文提升准确度

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json().get("text", "未能识别到文字")
        except Exception as e:
            return f"语音转换失败: {str(e)}"


    def get_score(self, question, answer, prompt_template=None, model="google/gemini-3-flash-preview"):
            # 默认模板
            default_template = """
            你是一位考公面试专家。请评价以下回答：
            题目：{question}
            回答：{answer}
            请给出：1. 维度评分 2. 优缺点分析 3. 改进版范文。
            """
            
            # 如果用户没传，用默认的；如果传了，确保它包含必要的占位符
            template = prompt_template if prompt_template else default_template
            
            try:
                # 使用 .format() 填充变量
                full_prompt = template.format(question=question, answer=answer)
            except KeyError as e:
                return f"Prompt 模板错误：缺少占位符 {str(e)}"

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "你是一个专业的公务员面试考官。"},
                        {"role": "user", "content": full_prompt}]
            )
            return response.choices[0].message.content