import json
import os

from playwright.sync_api import sync_playwright, TimeoutError
import math
import requests
from io import BytesIO
from PIL import Image


def get_aspect_ratio(url):
    response = requests.get(url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))

    width, height = image.size
    gcd = math.gcd(width, height)

    return f"{width // gcd}:{height // gcd}"


CHECKPOINT_FILE = "checkpoint.json"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            last_url = json.load(f).get("url")
            return last_url
    return None


def save_checkpoint(url):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"url": url}, f)


def launch_browser(playwright, url):
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

    context = browser.contexts[0]
    page = context.pages[0]

    page.goto(url)

    # input("Press Enter to start scraping...")
    return page


def scrape_liked_videos(playwright):
    results = []
    last_url = load_checkpoint()
    resuming = last_url is not None

    page = launch_browser(playwright, "https://www.youtube.com/playlist?list=LL")

    elements = page.locator('h3[role="presentation"]').locator("a").all()

    results = []
    for element in elements:
        link = f"https://www.youtube.com{element.get_attribute('href')}"
        if resuming:
            if link == last_url:
                resuming = False  # found where we left off
            continue  # skip until we pass the last processed item

        title = element.get_attribute("title")
        # thumbnail = (
        #     element.locator("yt-thumbnail-view-model")
        #     .locator("img")
        #     .get_attribute("src")
        # )
        # extract aspect ratio from thumbnail url to determine if it's a short
        # aspect_ratio = thumbnail.split("/")[4] if thumbnail else ""

        # is_short = "2∶3" in aspect_ratio
        page.goto(link)
        name = page.wait_for_selector(
            "a.ytAttributedStringLink.ytAttributedStringLinkCallToActionColor"
        ).inner_text()
        page.go_back()

        results.append(
            {
                "url": link,
                "name": name,
                "title": title,
                "thumbnail": None,
                "is_short": False,
            }
        )
        save_checkpoint(link)

    return results


def scrape_watchlater(playwright):
    page = launch_browser(playwright, "https://www.youtube.com/playlist?list=LW")
    results = []

    while True:

        try:

            with page.expect_response(
                lambda r: ("browse?prettyPrint=false" in r.url),
                timeout=10000,
            ) as response_info:

                page.keyboard.press("End")

            response = response_info.value

            data = {"url": response.url, "body": response.json()}

            results.append(data)

            print("FOUND:", response.url)

        except TimeoutError:
            print("No more responses found.")
            break

        except Exception as e:
            print("ERROR:", e)

    return results


with sync_playwright() as playwright:

    data = scrape_liked_videos(playwright)
    print(data)

    with open("liked_playlist.json", "w") as f:
        json.dump(data, f, indent=2)
