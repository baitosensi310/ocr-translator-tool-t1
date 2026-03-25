import easyocr

reader = easyocr.Reader(['ja'])

result = reader.readtext('test.png')

# 收集所有文字
texts = []

for item in result:
    text = item[1]
    texts.append(text)

# 合併成一句
final_text = "".join(texts)

print(final_text)