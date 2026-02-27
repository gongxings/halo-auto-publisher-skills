# Configuration

## Runtime

1. Python 3.10+.
2. Install dependency:

```powershell
pip install -r ./scripts/requirements.txt
```

## Required

1. `OPENAI_API_KEY`: API key for article and image generation.
2. `BING_API_KEY`: API key for Bing Web Search.
3. `BING_ENDPOINT`: Bing endpoint, e.g. `https://api.bing.microsoft.com`.
4. `HALO_BASE_URL`: Halo base URL, e.g. `https://halo.example.com`.
5. `HALO_TOKEN`: Halo API token.

## Optional

1. `OPENAI_BASE_URL`: default `https://api.openai.com/v1`.
2. `OPENAI_TEXT_MODEL`: default `gpt-4.1`.
3. `OPENAI_IMAGE_MODEL`: default `gpt-image-1`.
4. `HALO_UPLOAD_ENDPOINT`: default `/apis/api.console.halo.run/v1alpha1/attachments/upload`.
5. `HALO_POST_ENDPOINT`: default `/apis/api.console.halo.run/v1alpha1/posts`.
6. `DEFAULT_CATEGORY`: default category name.
7. `DEFAULT_TAGS`: comma-separated tags.
8. `DEFAULT_AUTHOR`: author display name.

## Config File (Recommended)

1. Copy `references/config.example.json` to your own path and fill values.
2. Run with `--config`:

```powershell
python ./scripts/run_pipeline.py --config ./references/config.example.json --prompt "你的主题"
```

3. CLI values can override config file:

```powershell
python ./scripts/run_pipeline.py --config ./references/config.example.json --prompt "你的主题" --halo-token "new-token"
```

## Environment Variable Example

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:BING_API_KEY="..."
$env:BING_ENDPOINT="https://api.bing.microsoft.com"
$env:HALO_BASE_URL="https://halo.example.com"
$env:HALO_TOKEN="..."
```
