import json

with open("data.json", "r") as f:
    data = json.load(f)
response = []
count = 0
for item in data:
    continuationItems = item["body"]["onResponseReceivedActions"][0][
        "appendContinuationItemsAction"
    ]["continuationItems"]
    for i, titles in enumerate(continuationItems):
        count += 1
        title = (
            titles.get("playlistVideoRenderer", {})
            .get("title", {})
            .get("runs", [{}])[0]
            .get("text")
        )
        channelName = (
            titles.get("playlistVideoRenderer", {})
            .get("shortBylineText", {})
            .get("runs", [{}])[0]
            .get("text")
        )
        videoLength = (
            titles.get("playlistVideoRenderer", {})
            .get("lengthText", {})
            .get("simpleText", {})
        )
        url = f"https://www.youtube.com/watch?v={titles.get('playlistVideoRenderer', {}).get('videoId', '')}"
        response.append(
            {
                "id": count,
                "title": title,
                "channelName": channelName,
                "videoLength": videoLength,
                "url": url,
            }
        )
with open("response.json", "w") as f:
    json.dump(response, f, indent=4)


def get_keys(obj, parent=""):
    keys = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{parent}.{key}" if parent else key
            keys.append(full_key)

            keys.extend(get_keys(value, full_key))

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            full_key = f"{parent}[{index}]"
            keys.extend(get_keys(item, full_key))

    return keys


# nested_keys = get_keys(data)

# print(nested_keys[0:200])
