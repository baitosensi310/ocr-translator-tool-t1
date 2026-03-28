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

    with open(JMDICT_PATH, "r", encoding="utf-8") as f:
        jmdict_data = json.load(f)

    return jmdict_data


def search_word(word):
    data = load_jmdict()

    results = []

    for entry in data:
        kanji_list = entry.get("kanji", [])
        kana_list = entry.get("kana", [])
        senses = entry.get("sense", [])

        # 比對漢字
        for k in kanji_list:
            if k.get("text") == word:
                results.append(entry)
                break

        # 比對假名
        for k in kana_list:
            if k.get("text") == word:
                results.append(entry)
                break

    return results


def extract_info(entry):
    """
    從 JMdict entry 抽出我們需要的資料
    """

    reading = ""
    english = ""
    part_of_speech = ""

    # 讀音
    kana_list = entry.get("kana", [])
    if kana_list:
        reading = kana_list[0].get("text", "")

    # 詞性 + 英文
    senses = entry.get("sense", [])
    if senses:
        first_sense = senses[0]

        # 英文
        gloss = first_sense.get("gloss", [])
        if gloss:
            english = "; ".join([g.get("text", "") for g in gloss if "text" in g])

        # 詞性
        pos = first_sense.get("partOfSpeech", [])
        if pos:
            part_of_speech = ", ".join(pos)

    return {
        "讀音": reading,
        "英文": english,
        "詞性": part_of_speech
    }