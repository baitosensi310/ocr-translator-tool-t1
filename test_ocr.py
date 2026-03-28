import easyocr
# list
reader = easyocr.Reader(['ja'])

result = reader.readtext('test.png')

# 收集所有文字
texts = []
#  ex:["你好", "世界"]
for item in result:
    text = item[1]
    texts.append(text)

# 合併成一句 分隔符（separator）
final_text = "".join(texts)

print(final_text)