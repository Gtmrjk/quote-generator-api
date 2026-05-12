import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.agent import QuoteGenerationError, generate_quote_image


app = FastAPI(
    title="Quote Image Generator API",
    version="1.0.0",
    description="Playwright-powered API wrapper around the DB Quote Image Generator UI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    image: UploadFile = File(..., description="PNG, JPG, JPEG, or WEBP image."),
    language: str = Form(..., description="English, Hindi, Marathi, or Gujarati."),
    quote: str = Form(..., max_length=250),
    name: str = Form("Author Name"),
    designation: str = Form("Designation"),
) -> Response:
    if image.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPG/JPEG, or WEBP image.")

    suffix = Path(image.filename or "upload.jpg").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".jpg"

    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = Path(tmp_dir) / f"input{suffix}"
        image_path.write_bytes(await image.read())

        try:
            jpg_bytes = await generate_quote_image(
                image_path=image_path,
                language=language,
                quote=quote,
                name=name,
                designation=designation,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except QuoteGenerationError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    return Response(
        content=jpg_bytes,
        media_type="image/jpeg",
        headers={"Content-Disposition": 'attachment; filename="quote-image.jpg"'},
    )
