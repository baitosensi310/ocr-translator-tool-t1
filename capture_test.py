from PIL import ImageGrab

# bbox = (左, 上, 右, 下)
# 這裡先隨便測一塊螢幕區域
bbox = (100, 100, 1200, 500)

img = ImageGrab.grab(bbox=bbox) # 截圖（在記憶體）
img.save("test.png") #存檔（寫到硬碟）

print("截圖完成，已存成 test.png")