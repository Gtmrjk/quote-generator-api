# Quote Image Generator API

This project wraps the published DB Quote Image Generator UI with a Playwright automation agent and exposes it as an HTTP API.

## UI Flow Mapped

The agent follows the site flow at `https://rose-arc-36021290.figma.site/`:

1. Upload image through `input[type=file]`.
2. Select domain from the dropdown:
   - `Hindi` -> `Bhaskar`
   - `Gujarati` -> `Divya Bhaskar`
   - `Marathi` -> `Divya Marathi`
   - `English` -> `English Bhaskar`
3. Fill quote, author name, and designation.
4. Click `Download JPG`.
5. Intercept the browser download and return `quote-image.jpg`.

## API

### `POST /generate`

Multipart form fields:

- `image`: PNG, JPG/JPEG, or WEBP file
- `language`: `English`, `Hindi`, `Marathi`, or `Gujarati`
- `quote`: quote text, max 250 characters
- `name`: author name
- `designation`: author designation

Example:

```bash
curl -X POST http://localhost:8000/generate \
  -F "image=@portrait.jpg" \
  -F "language=English" \
  -F "quote=The future belongs to those who build it." \
  -F "name=Jane Doe" \
  -F "designation=Founder" \
  --output quote-image.jpg
```

## Local Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the interactive API docs.

If your local browser install is restricted, use an existing Chrome binary:

```bash
CHROMIUM_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Render Deploy

Use the included `render.yaml`, or create a Render Web Service manually:

- Build command: `pip install -r requirements.txt && playwright install --with-deps chromium`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## GitHub

```bash
git init
git add .
git commit -m "Build Playwright quote generator API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/quote-generator-api.git
git push -u origin main
```
