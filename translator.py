from deep_translator import GoogleTranslator
from openai import OpenAI

# ⚠️ 這裡換成你的 OpenAI API Key
import os
from deep_translator import GoogleTranslator
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def translate_local(text):
    text = text.strip() #去除前後空白

    if not text:
        return "沒有可翻譯的文字"

    try:
        return GoogleTranslator(source="auto", target="zh-TW").translate(text)#翻譯成繁體中文
    except Exception as e:
        return f"本地翻譯失敗：{e}"


def translate_gpt(text):
    text = text.strip()

    if client is None:
        return "GPT翻譯失敗：尚未設定 OPENAI_API_KEY"

    if not text:
        return "沒有可翻譯的文字"

    try:
        response = client.chat.completions.create( #使用聊天模型進行翻譯
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "請將以下日文或英文翻譯成自然流暢的繁體中文。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"GPT翻譯失敗：{e}"


def translate(text, mode):
    if mode == "local":
        return translate_local(text)
    elif mode == "gpt":
        return translate_gpt(text)
    else:
        return "未知翻譯模式"