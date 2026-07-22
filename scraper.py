from playwright.sync_api import sync_playwright
import json


def check_json(response, results):

    if "browse?prettyPrint=false" in response.url:
        try:
            data = {"url": response.url, "body": response.json()}

            results.append(data)
            print("FOUND:", response.url)

        except Exception as e:
            print("Skipped:", response.url, e)


from playwright.sync_api import sync_playwright, TimeoutError
import json


def run(playwright):
    results = []

    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

    context = browser.contexts[0]
    page = context.pages[0]

    page.goto("https://www.youtube.com/playlist?list=WL")

    input("Press Enter to start scraping...")

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

    data = run(playwright)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
