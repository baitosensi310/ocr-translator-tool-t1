import json
import multiprocessing
import os
import re
from datetime import datetime

from language_detector import detect_language, is_ambiguous_cjk
from translator import translate_local
from jmdict_loader import search_word, extract_info

FILE_PATH = "dictionary.json"


def normalize_text(value):
    return str(value).replace("\u3000", " ").strip()


def normalize_tag_list(value):
    if not isinstance(value, list):
        return []

    result = []
    seen = set()

    for item in value:
        for text in re.split(r"[,，]", normalize_text(item)):
            text = normalize_text(text)
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


def create_empty_entry(word, language="unknown"):
    return {
        "language": language,
        "單字": word,
        "讀音": "",
        "中文": "",
        "英文": "",
        "詞性": "",
        "分類": [],
        "例句": [],
        "用法": "",
        "補充": "",
        "圖片": "",
        "左頁分割": [0.18, 0.42, 0.40],
        "加入時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def normalize_entry(item):
    # 防呆：不是 dict 就跳過，不要整本字典炸掉
    if not isinstance(item, dict):
        return None

    # 舊格式轉新格式
    if "單字" not in item:
        word = normalize_text(item.get("word", ""))
        meaning = normalize_text(item.get("meaning", ""))
        tag = normalize_text(item.get("tag", ""))

        if not word:
            return None

        return {
            "language": detect_language(word),
            "單字": word,
            "讀音": "",
            "中文": meaning,
            "英文": "",
            "詞性": "",
            "分類": [tag] if tag else [],
            "例句": [],
            "用法": "",
            "補充": "",
            "圖片": "",
            "左頁分割": [0.18, 0.42, 0.40],
            "加入時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    word = normalize_text(item.get("單字", ""))
    if not word:
        return None

    language = normalize_text(item.get("language", ""))
    if not language:
        language = detect_language(word)

    return {
        "language": language,
        "單字": word,
        "讀音": normalize_text(item.get("讀音", "")),
        "中文": normalize_text(item.get("中文", "")),
        "英文": normalize_text(item.get("英文", "")),
        "詞性": normalize_text(item.get("詞性", "")),
        "分類": normalize_tag_list(item.get("分類", [])),
        "例句": normalize_example_list(item.get("例句", [])),
        "用法": normalize_text(item.get("用法", "")),
        "補充": normalize_text(item.get("補充", "")),
        "圖片": normalize_text(item.get("圖片", "")),
        "左頁分割": item.get("左頁分割", [0.18, 0.42, 0.40]) if isinstance(item.get("左頁分割", [0.18, 0.42, 0.40]), list) else [0.18, 0.42, 0.40],
        "加入時間": normalize_text(item.get("加入時間", "")) or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def load_dictionary():
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("load_dictionary 讀取失敗：", e)
        return []

    if not isinstance(data, list):
        return []

    cleaned = []

    for item in data:
        try:
            new_item = normalize_entry(item)
            if new_item is not None:
                cleaned.append(new_item)
        except Exception as e:
            print("normalize_entry 失敗：", e, "item =", item)

    return cleaned


def save_dictionary(data):
    cleaned = []

    if not isinstance(data, list):
        data = []

    for item in data:
        try:
            new_item = normalize_entry(item)
            if new_item is not None:
                cleaned.append(new_item)
        except Exception as e:
            print("save_dictionary normalize 失敗：", e, "item =", item)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)


def is_probably_sentence(text):
    text = normalize_text(text)

    if not text:
        return False

    if len(text) >= 25:
        return True

    for mark in ["。", "、", "，", ",", "！", "？", "「", "」", "（", "）", "(", ")", " "]:
        if mark in text:
            return True

    return False


def translate_to_chinese(text):
    text = normalize_text(text)

    if not text:
        return ""

    try:
        translated = translate_local(text)
        translated = normalize_text(translated)

        if translated.startswith("本地翻譯失敗"):
            return ""

        return translated
    except Exception as e:
        print("translate_to_chinese 失敗：", e)
        return ""

JAPANESE_LOOKUP_TRANSLATION = str.maketrans({
    "國": "国",
    "際": "際",
})


def normalize_japanese_lookup_text(text):
    return normalize_text(text).translate(JAPANESE_LOOKUP_TRANSLATION)


def get_first_jmdict_info(word):
    results = search_word(word)
    if not results:
        return None

    info = extract_info(results[0])
    if not isinstance(info, dict):
        return None

    return {
        "讀音": normalize_text(info.get("讀音", "")),
        "英文": normalize_text(info.get("英文", "")),
        "詞性": normalize_text(info.get("詞性", ""))
    }


def find_jmdict_compound_info(word):
    word = normalize_japanese_lookup_text(word)
    if len(word) < 2:
        return None

    parts = []
    position = 0

    while position < len(word):
        matched = None

        for end in range(len(word), position, -1):
            part = word[position:end]
            info = get_first_jmdict_info(part)
            if info and info.get("讀音"):
                matched = {
                    "word": part,
                    "info": info
                }
                break

        if matched is None:
            return None

        parts.append(matched)
        position += len(matched["word"])

    if len(parts) <= 1:
        return None

    readings = [part["info"].get("讀音", "") for part in parts if part["info"].get("讀音", "")]
    english_list = [part["info"].get("英文", "") for part in parts if part["info"].get("英文", "")]
    pos_list = []

    for part in parts:
        pos = part["info"].get("詞性", "")
        if pos and pos not in pos_list:
            pos_list.append(pos)

    if not readings:
        return None

    return {
        "讀音": "".join(readings),
        "英文": " + ".join(english_list),
        "中文": translate_to_chinese(word),
        "詞性": " , ".join(pos_list)
    }


def find_jmdict_info(word):
    try:
        results = search_word(word)
        lookup_word = normalize_japanese_lookup_text(word)
        if not results and lookup_word != word:
            results = search_word(lookup_word)

        if not results:
            return find_jmdict_compound_info(word)

        readings = []
        english_list = []
        pos_list = []

        # 抓前3個結果（避免太亂）
        for entry in results[:3]:
            if not isinstance(entry, dict):
                continue

            info = extract_info(entry)
            if not isinstance(info, dict):
                continue

            r = normalize_text(info.get("讀音", ""))
            e = normalize_text(info.get("英文", ""))
            p = normalize_text(info.get("詞性", ""))

            if r and r not in readings:
                readings.append(r)

            if e and e not in english_list:
                english_list.append(e)

            if p and p not in pos_list:
                pos_list.append(p)

        # 中文先用日文翻
        chinese_text = translate_to_chinese(word)

        # 如果翻不到，用英文翻
        if not chinese_text and english_list:
            chinese_text = translate_to_chinese(english_list[0])

        return {
            "讀音": " / ".join(readings),
            "英文": " ; ".join(english_list),
            "中文": chinese_text,
            "詞性": " , ".join(pos_list)
        }

    except Exception as e:
        print("find_jmdict_info 失敗：", e)
        return None


def add_word(word, source_text="", forced_language=None):
    word = normalize_text(word)
    source_text = normalize_text(source_text)

    if not word:
        return "不能加入空白文字"

    if is_probably_sentence(word):
        return "這段內容看起來像句子，請先反白單字再加入"

    data = load_dictionary()

    for item in data:
        if item.get("單字", "") == word:
            return "已存在"

    if forced_language:
        language = forced_language
    else:
        word_language = detect_language(word)

        # 純漢字預設先當日文
        if word_language == "cjk":
            language = "ja"
        else:
            language = word_language

    new_entry = create_empty_entry(word, language=language)

    # 日文
    if language == "ja":
        info = find_jmdict_info(word)
        if info:
            new_entry["讀音"] = info.get("讀音", "")
            new_entry["英文"] = info.get("英文", "")
            new_entry["中文"] = info.get("中文", "")
            new_entry["詞性"] = info.get("詞性", "")

    # 英文
    elif language == "en":
        new_entry["英文"] = word
        new_entry["中文"] = translate_to_chinese(word)
        new_entry["詞性"] = "英文"

    # 中文
    elif language == "zh":
        new_entry["中文"] = word
        new_entry["詞性"] = "中文"

    # 韓文
    elif language == "ko":
        new_entry["中文"] = translate_to_chinese(word)
        new_entry["詞性"] = "韓文"

    # 其他
    else:
        new_entry["中文"] = translate_to_chinese(word)

    data.append(new_entry)
    save_dictionary(data)

    return f"已加入字典（語言：{language}）"

def delete_word(word):
    word = normalize_text(word)

    if not word:
        return "找不到單字"

    data = load_dictionary()
    new_data = []

    removed = False

    for item in data:
        if not removed and item.get("單字", "") == word:
            removed = True
            continue
        new_data.append(item)

    if not removed:
        return "找不到單字"

    save_dictionary(new_data)
    return "已刪除單字"

def add_word_fast(word, forced_language=None):
    word = normalize_text(word)

    if not word:
        return "不能加入空白文字"

    if is_probably_sentence(word):
        return "這段內容看起來像句子，請先反白單字再加入"

    data = load_dictionary()

    for item in data:
        if item.get("單字", "") == word:
            return "已存在"

    if forced_language:
        language = forced_language
    else:
        detected = detect_language(word)

        # 純漢字預設先當日文
        if detected == "cjk":
            language = "ja"
        else:
            language = detected

    new_entry = create_empty_entry(word, language=language)

    # 先只存最基本欄位，不查 JMdict，不翻譯
    if language == "zh":
        new_entry["中文"] = word
        new_entry["詞性"] = "中文"
    elif language == "en":
        new_entry["英文"] = word
        new_entry["詞性"] = "英文"
    elif language == "ko":
        new_entry["詞性"] = "韓文"

    data.append(new_entry)
    save_dictionary(data)

    return f"已加入字典（語言：{language}）"

def enrich_word_data(word):
    word = normalize_text(word)
    if not word:
        return "找不到單字"

    data = load_dictionary()

    target_index = None
    for i, item in enumerate(data):
        if item.get("單字", "") == word:
            target_index = i
            break

    if target_index is None:
        return "找不到單字"

    item = data[target_index]
    language = item.get("language", "unknown")

    # 日文補資料
    if language == "ja":
        info = find_jmdict_info(word)
        if info:
            if not item.get("讀音", ""):
                item["讀音"] = info.get("讀音", "")
            if not item.get("英文", ""):
                item["英文"] = info.get("英文", "")
            if not item.get("詞性", ""):
                item["詞性"] = info.get("詞性", "")

        # 中文最後補
        if not item.get("中文", ""):
            chinese_text = translate_to_chinese(word)

            if not chinese_text and item.get("英文", ""):
                chinese_text = translate_to_chinese(item.get("英文", ""))

            item["中文"] = chinese_text

    # 英文補中文
    elif language == "en":
        if not item.get("中文", ""):
            english_meaning = item.get("英文", "")

            if english_meaning:
                item["中文"] = translate_to_chinese(english_meaning)
            else:
                item["中文"] = translate_to_chinese(word)

    # 韓文補中文
    elif language == "ko":
        if not item.get("中文", ""):
            item["中文"] = translate_to_chinese(word)

    save_dictionary(data)
    return "已補完資料"

def enrich_word_data_async(word):
    process = multiprocessing.Process(
        target=enrich_word_data,
        args=(word,),
        daemon=True
    )
    process.start()
