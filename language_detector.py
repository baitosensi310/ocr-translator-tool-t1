import re


def detect_language(text):
    text = str(text).strip()

    if not text:
        return "unknown"

    # 日文假名
    if re.search(r"[\u3040-\u30ff]", text):
        return "ja"

    # 韓文
    if re.search(r"[\uac00-\ud7af]", text):
        return "ko"

    # 英文
    if re.search(r"[A-Za-z]", text) and not re.search(r"[\u4e00-\u9fff]", text):
        return "en"

    # 純漢字區
    if re.search(r"[\u4e00-\u9fff]", text):
        return "cjk"

    return "unknown"


def is_ambiguous_cjk(text):
    text = str(text).strip()
    if not text:
        return False

    # 只有漢字，沒有假名、沒有英文、沒有韓文
    has_cjk = re.search(r"[\u4e00-\u9fff]", text)
    has_kana = re.search(r"[\u3040-\u30ff]", text)
    has_latin = re.search(r"[A-Za-z]", text)
    has_hangul = re.search(r"[\uac00-\ud7af]", text)

    return bool(has_cjk and not has_kana and not has_latin and not has_hangul)