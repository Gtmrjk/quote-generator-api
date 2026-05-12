import asyncio
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


TOOL_URL = "https://rose-arc-36021290.figma.site/"

LANGUAGE_TO_DOMAIN = {
    "hindi": "bhaskar",
    "hi": "bhaskar",
    "bhaskar": "bhaskar",
    "gujarati": "divyabhaskar",
    "gu": "divyabhaskar",
    "divyabhaskar": "divyabhaskar",
    "marathi": "divyamarathi",
    "mr": "divyamarathi",
    "divyamarathi": "divyamarathi",
    "english": "englishbhaskar",
    "en": "englishbhaskar",
    "englishbhaskar": "englishbhaskar",
}


class QuoteGenerationError(RuntimeError):
    pass


def normalize_language(language: str) -> str:
    domain = LANGUAGE_TO_DOMAIN.get(language.strip().lower())
    if not domain:
        allowed = ", ".join(sorted({"English", "Hindi", "Marathi", "Gujarati"}))
        raise ValueError(f"Unsupported language '{language}'. Allowed values: {allowed}.")
    return domain


async def generate_quote_image(
    *,
    image_path: Path,
    language: str,
    quote: str,
    name: str,
    designation: str,
    tool_url: str = TOOL_URL,
    timeout_ms: int = 45_000,
    headless: bool = True,
) -> bytes:
    domain = normalize_language(language)
    image_path = image_path.resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    async with async_playwright() as p:
        launch_options = {
            "headless": headless,
            "args": ["--no-sandbox", "--disable-dev-shm-usage"],
        }
        executable_path = os.getenv("CHROMIUM_EXECUTABLE_PATH")
        if executable_path:
            launch_options["executable_path"] = executable_path

        browser = await p.chromium.launch(**launch_options)
        context = await browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 1100})
        page = await context.new_page()

        try:
            await page.goto(tool_url, wait_until="networkidle", timeout=timeout_ms)
            await page.locator("input[type='file']").set_input_files(str(image_path), timeout=timeout_ms)
            await page.locator("select").select_option(domain, timeout=timeout_ms)
            await page.locator("textarea").fill(quote, timeout=timeout_ms)

            text_inputs = page.locator("input[type='text']")
            await text_inputs.nth(0).fill(name, timeout=timeout_ms)
            await text_inputs.nth(1).fill(designation, timeout=timeout_ms)

            await page.wait_for_function(
                """
                () => {
                  const canvas = document.querySelector('canvas');
                  if (!canvas || canvas.width === 0 || canvas.height === 0) return false;
                  const ctx = canvas.getContext('2d');
                  const sample = ctx.getImageData(
                    Math.floor(canvas.width / 2),
                    Math.floor(canvas.height / 2),
                    1,
                    1
                  ).data;
                  return sample[3] > 0;
                }
                """,
                timeout=timeout_ms,
            )

            button = page.get_by_role("button", name=re.compile(r"Download JPG", re.I))
            async with page.expect_download(timeout=timeout_ms) as download_info:
                await button.click(timeout=timeout_ms)
            download = await download_info.value

            with tempfile.TemporaryDirectory() as tmp_dir:
                output_path = Path(tmp_dir) / (download.suggested_filename or "quote-image.jpg")
                await download.save_as(str(output_path))
                return output_path.read_bytes()
        except PlaywrightTimeoutError as exc:
            raise QuoteGenerationError("The quote generator UI did not respond in time.") from exc
        finally:
            await context.close()
            await browser.close()


def generate_quote_image_sync(**kwargs) -> bytes:
    return asyncio.run(generate_quote_image(**kwargs))
