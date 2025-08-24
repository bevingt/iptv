import requests
import re
import os
from datetime import datetime
from collections import defaultdict

# ------------------ 配置 ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
iptv_vlcopt_file = os.path.join(BASE_DIR, 'iptv_vlcopt.m3u')  # VLC / Kodi / PotPlayer 专用
iptv_ua_file = os.path.join(BASE_DIR, 'iptv_ua.m3u')          # URL 后追加 UA 的版本
iptv_tvbox_file = os.path.join(BASE_DIR, 'iptv_tvbox.txt')    # 影视仓 / TVBox 可用 TXT 文件

# 统一 UA 参数
ua = 'okHttp/Mod-1.1.0'

# 可选：更新时间对应的 URL，如果没有可留空或用占位 #
update_url = "#"

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
    fr'\1 #UA={ua}',
    original,
    flags=re.MULTILINE
)

with open(iptv_ua_file, "w", encoding="utf-8") as f:
    f.write(ua_text)

# ================== 版本3：生成影视仓 / TVBox 可用 TXT ==================

extinf_pattern = re.compile(r'#EXTINF:-?\d+.*,(?P<name>[^,]+)$')
group_pattern = re.compile(r'group-title="(.*?)"')

groups = defaultdict(list)  # {group_name: [(channel_name, url)]}

current_channel = None
current_group = None

for line in original.splitlines():
    line = line.strip()
    if line.startswith("#EXTINF"):
        # 提取频道名
        match_name = extinf_pattern.match(line)
        print(match_name)
        if match_name:
            current_channel = match_name.group(1).strip()  # 只取逗号后的频道名
            print(current_channel)
        # 提取分组
        match_group = group_pattern.search(line)
        if match_group:
            current_group = match_group.group(1).strip()
            print(current_group)
        else:
            current_group = "未分组"
    elif line and not line.startswith("#"):
        if current_channel:
            url_with_ua = f"{line}#user-agent={ua}"
            groups[current_group].append((current_channel, url_with_ua))
            current_channel = None
            current_group = None

# ------------------ 写入 TXT 文件 ------------------
with open(iptv_tvbox_file, "w", encoding="utf-8") as f:
    # 更新时间行
    f.write("更新时间,#genre#\n")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"{now_str},{update_url}\n\n")  # 这里的 URL 可自定义

    # 按分组输出
    for group_name, channels in groups.items():
        f.write(f"{group_name},#genre#\n")
        for channel_name, url in channels:
            f.write(f"{channel_name},{url}\n")
        f.write("\n")  # 分组间空行


# ------------------ 完成 ------------------
print("已生成三个文件：")
print(f"1. VLC/Kodi/PotPlayer 专用：{iptv_vlcopt_file}")
print(f"2. URL 后追加 UA：{iptv_ua_file}")
print(f"3. 影视仓/TVBox 可用 TXT：{iptv_tvbox_file}")
