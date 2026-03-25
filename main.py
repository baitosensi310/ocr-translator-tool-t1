from PIL import ImageGrab
import easyocr
from select_area import ScreenSelector
from result_window import ResultWindow


# =========================
# 1. 讓使用者手動拉框選區
# =========================
selector = ScreenSelector()
bbox = selector.get_area()

# 如果使用者按 ESC 或沒選區，就直接結束
if bbox is None:
    print("沒有選取範圍，程式結束")
    exit()

print("你選到的範圍：", bbox)


# =========================
# 2. 依照選到的範圍截圖
# =========================
img = ImageGrab.grab(bbox=bbox)
img.save("test.png")
print("截圖完成")


# =========================
# 3. 建立 OCR 引擎
# =========================
reader = easyocr.Reader(['ja'])


# =========================
# 4. 對截圖做 OCR
# =========================
result = reader.readtext("test.png")


# =========================
# 5. 收集文字
# =========================
texts = []

for item in result:
    text = item[1]
    texts.append(text)


# =========================
# 6. 合併成一句
# =========================
final_text = "".join(texts)


# =========================
# 7. 印出結果（保留給 debug）
# =========================
print("OCR 結果：")
print(final_text)


# =========================
# 8. 顯示結果視窗
# =========================
window = ResultWindow(final_text)
window.show()