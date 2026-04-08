import json
import os

JMDICT_PATH = "jmdict.json"

jmdict_data = None


def load_jmdict():
    global jmdict_data

    if jmdict_data is not None:
        return jmdict_data

    if not os.path.exists(JMDICT_PATH):
        print("找不到 jmdict.json")
        return []

    try:
        with open(JMDICT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("讀取 jmdict.json 失敗：", e)
        return []

    # 有些 json 可能外層不是 list
    if isinstance(data, list):
        jmdict_data = data
    elif isinstance(data, dict):
        # 如果你的 jmdict.json 外層是 dict，常見可能在 words / entries
        if isinstance(data.get("words"), list):
            jmdict_data = data["words"]
        elif isinstance(data.get("entries"), list):
            jmdict_data = data["entries"]
        else:
            jmdict_data = []
    else:
        jmdict_data = []

    return jmdict_data

def search_word(word):
    data = load_jmdict()
    results = []

    word = str(word).strip()
    if not word:
        return results

    for entry in data:
        if not isinstance(entry, dict):
            continue

        kanji_list = entry.get("kanji", [])
        kana_list = entry.get("kana", [])

        if isinstance(kanji_list, list):
            for k in kanji_list:
                if isinstance(k, dict) and str(k.get("text", "")).strip() == word:
                    results.append(entry)
                    return results   # 找到第一筆就先回傳，先不要全掃完

        if isinstance(kana_list, list):
            for k in kana_list:
                if isinstance(k, dict) and str(k.get("text", "")).strip() == word:
                    results.append(entry)
                    return results   # 找到第一筆就先回傳

    return results

def extract_info(entry):
    if not isinstance(entry, dict):
        return {
            "讀音": "",
            "英文": "",
            "詞性": ""
        }

    reading = ""
    english = ""
    part_of_speech = ""

    kana_list = entry.get("kana", [])
    if isinstance(kana_list, list) and kana_list:
        first_kana = kana_list[0]
        if isinstance(first_kana, dict):
            reading = first_kana.get("text", "")

    senses = entry.get("sense", [])
    if isinstance(senses, list) and senses:
        first_sense = senses[0]

        if isinstance(first_sense, dict):
            gloss = first_sense.get("gloss", [])
            if isinstance(gloss, list):
                english_list = []
                for g in gloss:
                    if isinstance(g, dict) and "text" in g:
                        english_list.append(g["text"])
                    elif isinstance(g, str):
                        english_list.append(g)

                english = "; ".join(english_list)

            pos = first_sense.get("partOfSpeech", [])
            if isinstance(pos, list):
                part_of_speech = ", ".join([str(x) for x in pos])

    return {
        "讀音": reading,
        "英文": english,
        "詞性": part_of_speech
    }