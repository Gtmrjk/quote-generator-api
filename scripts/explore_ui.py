import asyncio
import json
import os

from playwright.async_api import async_playwright


URL = "https://rose-arc-36021290.figma.site/"


async def main() -> None:
    async with async_playwright() as p:
        launch_options = {"headless": True, "args": ["--no-sandbox"]}
        executable_path = os.getenv("CHROMIUM_EXECUTABLE_PATH")
        if executable_path:
            launch_options["executable_path"] = executable_path
        browser = await p.chromium.launch(**launch_options)
        page = await browser.new_page(viewport={"width": 1440, "height": 1100})
        await page.goto(URL, wait_until="networkidle")

        controls = await page.evaluate(
            """
            () => [...document.querySelectorAll('input, select, textarea, button, canvas')].map((el, index) => ({
              index,
              tag: el.tagName.toLowerCase(),
              type: el.getAttribute('type'),
              text: el.innerText || el.value || '',
              options: el.tagName === 'SELECT'
                ? [...el.options].map(option => ({ value: option.value, label: option.textContent }))
                : undefined
            }))
            """
        )
        print(json.dumps(controls, indent=2))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
