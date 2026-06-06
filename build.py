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
    Lightweight check (header-based)
    """
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)

        if r.status_code != 200:
            return False

        ctype = r.headers.get("Content-Type", "")
        return (
            "video" in ctype
            or "mpegurl" in ctype
            or "application" in ctype
        )

    except:
        return False


def clean_line(line):
    return line.strip()


print("Building CLEAN stable playlist...")

seen = set()
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

            # -----------------------------
            # Extract tvg-id (best ID)
            # -----------------------------
            tvg_id = ""
            if 'tvg-id="' in current_extinf:
                try:
                    tvg_id = current_extinf.split('tvg-id="')[1].split('"')[0].strip().lower()
                except:
                    tvg_id = ""

            # -----------------------------
            # Extract channel name
            # -----------------------------
            channel_name = current_extinf.split(",")[-1].strip().lower()

            # -----------------------------
            # Unique identity key
            # (THIS fixes PRO TV RO vs MD)
            # -----------------------------
            unique_key = tvg_id if tvg_id else channel_name

            if unique_key in seen:
                continue

            print(f"Testing: {line[:60]}...")

            if is_stream_alive(line):
                seen.add(unique_key)
                output.append(current_extinf)
                output.append(line)
            else:
                print("  ❌ dead stream skipped")

            time.sleep(0.2)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Done. Clean playlist written: {OUTPUT_FILE}")
print(f"Total channels: {len(seen)}")
