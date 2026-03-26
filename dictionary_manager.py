import json
import os

FILE_PATH = "dictionary.json"


def load_dictionary():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dictionary(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_word(word):
    data = load_dictionary()

    for item in data:
        if item["word"] == word:
            return "已存在"

    new_entry = {
        "word": word,
        "meaning": "",
        "tag": ""
    }

    data.append(new_entry)
    save_dictionary(data)

    return "已加入字典"