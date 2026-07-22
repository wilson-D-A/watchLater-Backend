import json
import pathlib

new_json = pathlib.Path("api") / "watchlater_grouped.json"
old_json = pathlib.Path("api") / "watchlater_old.json"

with open(new_json, "r") as f:
    data = json.load(f)
    print(f"Loaded {len(data)} JSON objects from {new_json}")
with open(old_json, "r") as f:
    old_data = json.load(f)
    print(f"Loaded {len(old_data)} JSON objects from {old_json}")

for item in data:
    for old_item in old_data:
        for video in old_item["videos"]:
            if item["title"] == video["title"]:
                print(item["tag"], video.get("subcategory", []))
                item["tag"] = video.get("subcategory", [])


with open(new_json, "w") as f:
    json.dump(data, f, indent=4)
    print(f"Saved merged JSON objects to {new_json}")
