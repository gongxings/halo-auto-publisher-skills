---
name: halo-article-publisher
description: Publish a Markdown article to Halo with optional image handling. Use when user provides a ready article and wants to upload it to Halo: upload local images, set cover, and publish or save as draft.
---

# Halo Article Publisher

Publish an existing Markdown article to Halo.

## Quick Start

1. Set required environment variables:
   - `HALO_BASE_URL`: Halo site URL
   - `HALO_TOKEN`: Admin token

2. Publish an article:

```bash
python ./scripts/run_pipeline.py \
  --article "path/to/article.md" \
  --publish-status PUBLISHED
```

3. With images:

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --publish-status PUBLISHED
```

## Default Behavior

1. Parse title from first `# heading` in Markdown.
2. Upload cover image if provided.
3. Scan article for local image references `![alt](path)` and upload them to Halo, replacing URLs.
4. Publish or save as draft.

## Arguments

- `--article` (required): Path to the Markdown file
- `--images-dir`: Directory containing images referenced in the article (optional)
- `--cover`: Cover image file path (optional)
- `--publish-status`: `PUBLISHED` or `DRAFT` (default: PUBLISHED)
- `--halo-base-url`: Override `HALO_BASE_URL` env var
- `--halo-token`: Override `HALO_TOKEN` env var

## Notes

1. Article generation is done by LLM outside this tool.
2. Images must exist locally; they will be uploaded to Halo and URLs replaced.
3. Only the `halo_client.py` module handles Halo API interactions.
