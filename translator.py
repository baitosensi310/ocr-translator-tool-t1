from deep_translator import GoogleTranslator
from openai import OpenAI

# ⚠️ 這裡換成你的 OpenAI API Key
client = OpenAI(api_key="你的APIKEY")


def translate_local(text):
    text = text.strip()

    if not text:
        return "沒有可翻譯的文字"

    try:
        return GoogleTranslator(source="auto", target="zh-TW").translate(text)
    except Exception as e:
        return f"本地翻譯失敗：{e}"


def translate_gpt(text):
    text = text.strip()

    if not text:
        return "沒有可翻譯的文字"

    try:
        response = client.chat.completions.create(
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