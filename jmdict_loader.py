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

    if isinstance(data, list):
        jmdict_data = data
    elif isinstance(data, dict):
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
    seen_ids = set()

    word = str(word).strip()
    if not word:
        return results

    for entry in data:
        if not isinstance(entry, dict):
            continue

        kanji_list = entry.get("kanji", [])
        kana_list = entry.get("kana", [])

        matched = False

        if isinstance(kanji_list, list):
            for k in kanji_list:
                if isinstance(k, dict) and str(k.get("text", "")).strip() == word:
                    matched = True
                    break

        if not matched and isinstance(kana_list, list):
            for k in kana_list:
                if isinstance(k, dict) and str(k.get("text", "")).strip() == word:
                    matched = True
                    break

        if matched:
            entry_key = json.dumps(entry, ensure_ascii=False, sort_keys=True)
            if entry_key not in seen_ids:
                results.append(entry)
                seen_ids.add(entry_key)

    return results


def extract_info(entry):
    if not isinstance(entry, dict):
        return {
            "讀音": "",
            "英文": "",
            "詞性": ""
        }

    readings = []
    english_list = []
    pos_list = []

    kana_list = entry.get("kana", [])
    if isinstance(kana_list, list):
        for kana in kana_list:
            if isinstance(kana, dict):
                text = str(kana.get("text", "")).strip()
                if text and text not in readings:
                    readings.append(text)

    senses = entry.get("sense", [])
    if isinstance(senses, list):
        for sense in senses:
            if not isinstance(sense, dict):
                continue

            gloss = sense.get("gloss", [])
            if isinstance(gloss, list):
                for g in gloss:
                    if isinstance(g, dict):
                        gloss_lang = str(g.get("lang", "")).strip().lower()
                        if gloss_lang and gloss_lang not in {"eng", "en"}:
                            continue
                        text = str(g.get("text", "")).strip()
                    else:
                        text = str(g).strip()

                    if text and text not in english_list:
                        english_list.append(text)

            pos = sense.get("partOfSpeech", [])
            if isinstance(pos, list):
                for p in pos:
                    text = str(p).strip()
                    if text and text not in pos_list:
                        pos_list.append(text)

    return {
        "讀音": " / ".join(readings),
        "英文": "; ".join(english_list),
        "詞性": ", ".join(pos_list)
    }
