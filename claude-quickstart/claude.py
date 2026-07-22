import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

BATCH_SIZE = 25
MAX_OUTPUT_TOKENS = 8192
MODEL = "claude-opus-4-8"

OUTPUT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "channelName": {"type": "string"},
            "videoLength": {"type": "string"},
            "url": {"type": "string"},
            "category": {"type": "string"},
            "tag": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "id",
            "title",
            "channelName",
            "videoLength",
            "url",
            "category",
            "tag",
        ],
        "additionalProperties": False,
    },
}


def get_text_content(message):
    text_blocks = [block.text for block in message.content if block.type == "text"]
    if not text_blocks:
        raise ValueError("Claude response did not contain any text blocks")
    return "".join(text_blocks)


def classify_batch(client, items):
    payload = json.dumps(items, indent=2)
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"""
Here is the JSON data:

{payload}

Act as an expert organizer. Using the list of JSON objects, group each object into one of the following categories that best describe the object: "Core Programming", "Frontend", "Backend", "Cloud & DevOps", "Computer Science", "Engineering Practices", "AI", "Career", "Personal Development", "Miscellaneous".

Add the category to a "category" key. Add a "tag" key where the value is an array of exactly three strings in this order: [concept, tool, topic]. Return only the updated list of JSON objects.""",
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": OUTPUT_SCHEMA,
            }
        },
    )
    return json.loads(get_text_content(message))


def main():
    json_path = Path(__file__).parent.parent / "response.json"
    output_path = Path(__file__).parent.parent / "claude.json"

    with open(json_path, "r") as file:
        json_content = json.load(file)

    print(f"Loaded {len(json_content)} JSON objects from {json_path}")

    load_dotenv()
    my_api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=my_api_key)

    classified_items = []
    total_batches = (len(json_content) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_index in range(total_batches):
        start = batch_index * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = json_content[start:end]
        print(
            f"Processing batch {batch_index + 1}/{total_batches} "
            f"for items {start + 1}-{start + len(batch)}"
        )
        classified_batch = classify_batch(client, batch)
        if len(classified_batch) != len(batch):
            raise ValueError(
                "Claude returned an unexpected number of objects for "
                f"batch {batch_index + 1}: expected {len(batch)}, got {len(classified_batch)}"
            )
        classified_items.extend(classified_batch)

    with open(output_path, "w") as file:
        json.dump(classified_items, file, indent=2)

    print(f"Wrote {len(classified_items)} JSON objects to {output_path}")


if __name__ == "__main__":
    main()
