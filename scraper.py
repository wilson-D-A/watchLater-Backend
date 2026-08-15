import json
import os
from playwright.sync_api import TimeoutError, sync_playwright
from playwright.sync_api import TimeoutError
import math
import requests
from io import BytesIO
from PIL import Image
from pprint import pprint


def get_aspect_ratio(url):
    if url is None:
        return None

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

    elements = page.locator("#content").all()

    results = []
    try:
        for element in elements:
            presentation = element.locator("h3[role='presentation']")
            link = f"https://www.youtube.com{presentation.locator('a').first.get_attribute('href')}"
            if resuming:
                if link == last_url:
                    resuming = False  # found where we left off
                continue  # skip until we pass the last processed item
            title = presentation.locator("a").first.get_attribute("title")
            element.scroll_into_view_if_needed()
            element.locator("img").first.wait_for(state="attached", timeout=10000)
            thumbnail = (
                element.locator(".ytThumbnailViewModelImage")
                .locator("img")
                .first.get_attribute("src")
            )

            aspect_ratio = get_aspect_ratio(thumbnail)
            is_short = aspect_ratio in {"405:608", "2:3"}
            page.goto(link)
            name = page.wait_for_selector(
                "a.ytAttributedStringLink.ytAttributedStringLinkCallToActionColor"
            ).inner_text()
            page.go_back()

            data = {
                "url": link,
                "name": name,
                "title": title,
                "thumbnail": thumbnail,
                "is_short": is_short,
            }
            results.append(data)
            pprint(data)
    except Exception as e:
        print("ERROR:", e)

        with open("liked_playlist.json", "a") as f:
            json.dump(results, f, indent=2)

    with open("liked_playlist.json", "a") as f:
        json.dump(results, f, indent=2)

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
