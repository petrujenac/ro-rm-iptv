import requests
import time
import re

SOURCES = [
    "https://iptv-org.github.io/iptv/countries/ro.m3u",
    "https://iptv-org.github.io/iptv/languages/ron.m3u",
    "https://iptv-org.github.io/iptv/countries/md.m3u",
    "https://wlog.ro/api/iptv.m3u"
]

OUTPUT_FILE = "ron.m3u"
TIMEOUT = 6


def is_stream_alive(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)
        if r.status_code != 200:
            return False

        ctype = r.headers.get("Content-Type", "")
        return any(x in ctype for x in ["video", "mpegurl", "application"])
    except:
        return False


def clean_name(extinf_line):
    """
    Extracts channel name from #EXTINF line for better deduping.
    """
    # last part after comma is channel name
    return extinf_line.split(",")[-1].strip().lower()


def normalize_key(name, url):
    """
    Smart key:
    - keeps same-name channels only if truly identical stream
    - avoids mixing RO vs MD versions incorrectly
    """
    # country hint (simple heuristic)
    if ".md" in url or "moldova" in name:
        country = "md"
    elif ".ro" in url or "romania" in name:
        country = "ro"
    else:
        country = "global"

    # remove HD/SD noise
    name = re.sub(r"\b(hd|sd|fhd|uhd|4k|1080p|720p)\b", "", name).strip()

    return f"{country}:{name}"


print("Building CLEAN stable playlist...")

seen_urls = set()
seen_channels = set()

output = []
output.append('#EXTM3U x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_RO1.xml.gz"')

for src in SOURCES:
    print(f"\nFetching: {src}")

    try:
        data = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"Failed source: {src} -> {e}")
        continue

    current_extinf = None

    for line in data:
        line = line.strip()

        if line.startswith("#EXTINF"):
            current_extinf = line

        elif line.startswith("http"):
            if not current_extinf:
                continue

            url = line
            name = clean_name(current_extinf)
            key = normalize_key(name, url)

            # skip obvious junk
            if any(x in url for x in ["example.com", "127.0.0.1", "localhost"]):
                continue

            # prevent exact duplicates
            if url in seen_urls:
                continue

            print(f"Testing: {name[:50]}")

            if is_stream_alive(url):
                seen_urls.add(url)

                # only block exact same channel in same region
                if key in seen_channels:
                    continue

                seen_channels.add(key)

                output.append(current_extinf)
                output.append(url)
            else:
                print("  ❌ dead stream skipped")

            time.sleep(0.15)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output))


print(f"\nDone. Playlist written: {OUTPUT_FILE}")
print(f"Total channels: {len(seen_channels)}")
