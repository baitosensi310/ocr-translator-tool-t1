import re


def detect_language(text):
    text = str(text).strip()

    if not text:
        return "unknown"

    if re.search(r"[\u3040-\u30ff]", text):
        return "ja"

    if re.search(r"[\uac00-\ud7af]", text):
        return "ko"

    if re.search(r"[A-Za-z]", text) and not re.search(r"[\u4e00-\u9fff]", text):
        return "en"

    if re.search(r"[\u4e00-\u9fff]", text):
        return "cjk"

    return "unknown"


def is_ambiguous_cjk(text):
    text = str(text).strip()

    if not text:
        return False

    has_cjk = re.search(r"[\u4e00-\u9fff]", text)
    has_kana = re.search(r"[\u3040-\u30ff]", text)
    has_latin = re.search(r"[A-Za-z]", text)
    has_hangul = re.search(r"[\uac00-\ud7af]", text)

    return bool(has_cjk and not has_kana and not has_latin and not has_hangul)