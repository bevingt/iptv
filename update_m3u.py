import requests
import re
import os

# ------------------ 配置 ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
iptv_vlcopt_file = os.path.join(BASE_DIR, 'iptv_vlcopt.m3u')  # VLC / Kodi / PotPlayer 专用
iptv_ua_file = os.path.join(BASE_DIR, 'iptv_ua.m3u')          # URL 后追加 UA 的版本

# 统一 UA 参数
ua = 'okHttp/Mod-1.2.0'

# IPTV 源链接
url = "https://raw.githubusercontent.com/mursor1985/LIVE/refs/heads/main/iptv.m3u"

# ------------------ 获取原始内容 ------------------
original = requests.get(url, timeout=10).text

# ================== 版本1：在 #EXTINF 后插入 #EXTVLCOPT（VLC/Kodi/PotPlayer） ==================
lines = original.splitlines()
vlc_lines = []

for i, line in enumerate(lines):
    vlc_lines.append(line)
    if line.startswith("#EXTINF:") and i + 1 < len(lines):
        next_line = lines[i + 1].strip()
        # 如果下一行是播放地址，则插入 UA 标签
        if next_line and not next_line.startswith("#"):
            vlc_lines.append(f'#EXTVLCOPT:http-user-agent={ua}')

with open(iptv_vlcopt_file, "w", encoding="utf-8") as f:
    f.write("\n".join(vlc_lines))

# ================== 版本2：在 URL 后追加 #UA=（IPTV-API / 工具箱 / Pixman） ==================
ua_text = re.sub(
    r'^(https?://.+\.m3u8\S*)$',
    fr'\1?ua={ua}',
    original,
    flags=re.MULTILINE
)

with open(iptv_ua_file, "w", encoding="utf-8") as f:
    f.write(ua_text)


# ------------------ 完成 ------------------
print("已生成2个文件：")
print(f"1. VLC/Kodi/PotPlayer 专用：{iptv_vlcopt_file}")
print(f"2. URL 后追加 UA：{iptv_ua_file}")
