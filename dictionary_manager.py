import json
import os
import re

from jmdict_loader import search_word, extract_info

FILE_PATH = "dictionary.json"


def create_empty_entry(word):
    return {
        "單字": word,
        "讀音": "",
        "中文": "",
        "英文": "",
        "詞性": "",
        "分類": [],
        "例句": [],
        "用法": ""
    }


def normalize_text(value):
    return str(value).replace("\u3000", " ").strip()


def normalize_tag_list(value):
    if not isinstance(value, list):
        return []

    result = []
    seen = set()

    for item in value:
        text = normalize_text(item)
        if text and text not in seen:
            result.append(text)
            seen.add(text)

    return result


def normalize_example_list(value):
    if not isinstance(value, list):
        return []

    result = []
    for item in value:
        text = normalize_text(item)
        if text:
            result.append(text)

    return result


def normalize_entry(item):
    # 防呆：如果 item 不是 dict，直接跳過
    if not isinstance(item, dict):
        return None

    # 舊格式轉新格式
    if "單字" not in item:
        word = normalize_text(item.get("word", ""))
        meaning = normalize_text(item.get("meaning", ""))
        tag = normalize_text(item.get("tag", ""))

        return {
            "單字": word,
            "讀音": "",
            "中文": meaning,
            "英文": "",
            "詞性": "",
            "分類": [tag] if tag else [],
            "例句": [],
            "用法": ""
        }

    word = normalize_text(item.get("單字", ""))
    if not word:
        return None

    return {
        "單字": word,
        "讀音": normalize_text(item.get("讀音", "")),
        "中文": normalize_text(item.get("中文", "")),
        "英文": normalize_text(item.get("英文", "")),
        "詞性": normalize_text(item.get("詞性", "")),
        "分類": normalize_tag_list(item.get("分類", [])),
        "例句": normalize_example_list(item.get("例句", [])),
        "用法": normalize_text(item.get("用法", ""))
    }


def load_dictionary():
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    cleaned = []

    for item in data:
        new_item = normalize_entry(item)
        if new_item is not None:
            cleaned.append(new_item)

    return cleaned


def save_dictionary(data):
    cleaned = []

    if not isinstance(data, list):
        data = []

    for item in data:
        new_item = normalize_entry(item)
        if new_item is not None:
            cleaned.append(new_item)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)


def is_probably_sentence(text):
    text = normalize_text(text)

    if len(text) >= 25:
        return True

    for mark in ["。", "、", "，", ",", "！", "？", "「", "」", "（", "）", "(", ")", " "]:
        if mark in text:
            return True

    return False


def find_jmdict_info(word):
    try:
        results = search_word(word)
        if not results:
            return None

        first_entry = results[0]

        # 防呆：不是 dict 就不要往下處理
        if not isinstance(first_entry, dict):
            return None

        info = extract_info(first_entry)
        if not isinstance(info, dict):
            return None

        return {
            "讀音": normalize_text(info.get("讀音", "")),
            "英文": normalize_text(info.get("英文", "")),
            "詞性": normalize_text(info.get("詞性", ""))
        }
    except Exception as e:
        print("find_jmdict_info error:", e)
        return None


def add_word(word):
    word = normalize_text(word)

    if not word:
        return "不能加入空白文字"

    if is_probably_sentence(word):
        return "這段內容看起來像句子，請先反白單字再加入"

    data = load_dictionary()

    for item in data:
        if item.get("單字", "") == word:
            return "已存在"

    new_entry = create_empty_entry(word)

    info = find_jmdict_info(word)
    if info:
        new_entry["讀音"] = info["讀音"]
        new_entry["英文"] = info["英文"]
        new_entry["詞性"] = info["詞性"]

    data.append(new_entry)
    save_dictionary(data)

    if info:
        return "已加入字典（已自動補讀音/英文/詞性）"
    return "已加入字典（找不到 JMdict 資料）"