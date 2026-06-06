import requests
import time

SOURCES = [
    "https://iptv-org.github.io/iptv/countries/ro.m3u",
    "https://iptv-org.github.io/iptv/languages/ron.m3u",
    "https://iptv-org.github.io/iptv/countries/md.m3u",
    "https://wlog.ro/api/iptv.m3u"
]

OUTPUT_FILE = "ron.m3u"
TIMEOUT = 6

def is_stream_alive(url):
    """
    Lightweight check:
    We only test headers (fast, avoids hanging on slow streams).
    """
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)
        if r.status_code != 200:
            return False
        ctype = r.headers.get("Content-Type", "")
        # most HLS streams are video or binary chunks
        return "video" in ctype or "mpegurl" in ctype or "application" in ctype
    except:
        return False

def clean_line(line):
    return line.strip()

print("Building CLEAN stable playlist...")

seen_streams = set()
output = []

output.append('#EXTM3U x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_RO1.xml.gz"\n')

for src in SOURCES:
    print(f"Fetching: {src}")

    try:
        data = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"Failed source: {src} -> {e}")
        continue

    current_extinf = None

    for line in data:
        line = clean_line(line)

        if line.startswith("#EXTINF"):
            current_extinf = line

        elif line.startswith("http"):
            if not current_extinf:
                continue

            if line in seen_streams:
                continue

            # skip obvious bad sources
            if any(x in line for x in [
                "example.com",
                "127.0.0.1",
                "localhost"
            ]):
                continue

            print(f"Testing: {line[:60]}...")

            if is_stream_alive(line):
                seen_streams.add(line)
                output.append(current_extinf)
                output.append(line)
            else:
                print("  ❌ dead stream skipped")

            time.sleep(0.2)  # avoid hammering servers

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Done. Clean playlist written: {OUTPUT_FILE}")
print(f"Total channels: {len(seen_streams)}")
