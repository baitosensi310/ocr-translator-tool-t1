import easyocr

try:
    from manga_ocr import MangaOcr
except ImportError:
    MangaOcr = None


class OCREngine:
    def __init__(self):
        self.easy_reader = None
        self.manga_reader = None

    def read_easyocr(self, image_path):
        if self.easy_reader is None:
            self.easy_reader = easyocr.Reader(["ja", "en"]) #texts = ["你好", "世界"]

        result = self.easy_reader.readtext(image_path)

        texts = []
        for item in result:
            texts.append(item[1]) 

        return "".join(texts) #"你好世界" 分隔符（separator）

    def read_mangaocr(self, image_path):
        if MangaOcr is None:
            return "Manga-OCR 尚未安裝，請先執行：python -m pip install manga-ocr"

        if self.manga_reader is None:
            self.manga_reader = MangaOcr()

        return self.manga_reader(image_path)

    def read(self, image_path, mode):
        print("目前 OCR 模式：", mode)

        if mode == "easyocr":
            print("使用 EasyOCR")
            return self.read_easyocr(image_path)

        elif mode == "mangaocr":
            print("使用 Manga-OCR")
            return self.read_mangaocr(image_path)

        else:
            return "未知 OCR 模式"