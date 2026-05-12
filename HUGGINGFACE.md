# Deploy on Hugging Face Spaces

Use a Docker Space for this API because Playwright needs a browser runtime.

## Steps

1. Go to `https://huggingface.co/new-space`.
2. Choose:
   - Space name: `quote-generator-api`
   - SDK: `Docker`
   - Hardware: `CPU Basic`
   - Visibility: Public or Private
3. Create the Space.
4. Upload or sync these repo files to the Space.
5. Hugging Face will build the Docker image and expose the API on port `7860`.

## Test

After the Space is running:

```bash
curl -X POST https://YOUR_USERNAME-quote-generator-api.hf.space/generate \
  -F "image=@portrait.jpg" \
  -F "language=English" \
  -F "quote=The future belongs to those who build it." \
  -F "name=Jane Doe" \
  -F "designation=Founder" \
  --output quote-image.jpg
```

Health check:

```bash
curl https://YOUR_USERNAME-quote-generator-api.hf.space/health
```
