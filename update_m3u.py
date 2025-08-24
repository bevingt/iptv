import requests
import re

# 获取mursor的LIVE仓库iptv.m3u
url = "https://raw.githubusercontent.com/mursor1985/LIVE/refs/heads/main/iptv.m3u"
response = requests.get(url)
content = response.text

# 正则匹配所有.m3u8结尾的URL，并在其后添加指定字符串
pattern = re.compile(r'(https?://[^\s]+\.m3u8)(\?[^\s]*)?')
modified_content = pattern.sub(r'\1\2|ua=okHttp/Mod-1.1.0', content)

# 保存到本地新文件
with open("modified_iptv.m3u", "w", encoding="utf-8") as file:
    file.write(modified_content)

print("已生成修改后的播放列表：modified_iptv.m3u")
