import requests

SOURCES = [
    "https://iptv-org.github.io/iptv/countries/ro.m3u",
    "https://iptv-org.github.io/iptv/languages/ron.m3u"
]

OUTPUT_FILE = "ron.m3u"

def is_valid_stream(line: str) -> bool:
    return line.startswith("http")

def is_valid_extinf(line: str) -> bool:
    return line.startswith("#EXTINF")

seen = set()

print("Starting playlist build...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write('#EXTM3U x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_RO1.xml.gz"\n\n')

    for src in SOURCES:
        print(f"Fetching: {src}")
        try:
            data = requests.get(src, timeout=30).text.splitlines()
        except Exception as e:
            print(f"Failed to fetch {src}: {e}")
            continue

        current_extinf = None

        for line in data:
            line = line.strip()

            if is_valid_extinf(line):
                current_extinf = line

            elif is_valid_stream(line):
                if current_extinf and line not in seen:
                    # filter obvious invalid recursive entries
                    if "iptv-org.github.io" in line:
                        continue

                    seen.add(line)
                    out.write(current_extinf + "\n")
                    out.write(line + "\n")

print(f"Done. Channels written to {OUTPUT_FILE}")
