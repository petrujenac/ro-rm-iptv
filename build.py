import requests

SOURCES = [
    "https://iptv-org.github.io/iptv/countries/ro.m3u",
    "https://iptv-org.github.io/iptv/languages/ron.m3u"
]

OUTPUT = "ron.m3u"

seen = set()

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write('#EXTM3U x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_RO1.xml.gz"\n\n')

    for url in SOURCES:
        data = requests.get(url, timeout=30).text.splitlines()

        last = None

        for line in data:
            line = line.strip()

            if line.startswith("#EXTINF"):
                last = line

            elif line.startswith("http"):
                if line not in seen:
                    seen.add(line)

                    # filter obvious broken/self-referential entries
                    if "iptv-org.github.io" in line:
                        continue

                    f.write(last + "\n")
                    f.write(line + "\n")
