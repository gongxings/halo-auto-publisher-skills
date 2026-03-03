---
name: halo-article-publisher
description: Publish a Markdown article to Halo blog with full SVG support, content optimization, and automatic image handling. Use when user provides a ready article and wants to upload it to Halo: upload local images (including SVG→PNG conversion), set cover, and publish or save as draft.
version: 2.0.0
tags:
  - publishing
  - blog
  - halo
  - markdown
  - images
  - svg
  - content-optimization
author: gongxings
---

# Halo Article Publisher v2.0

Publish an existing Markdown article to Halo blog platform with full Halo 2.x support, automatic SVG conversion, and content optimization.

## ✨ New in v2.0

- **🖼️ SVG Support**: Automatically convert embedded `<svg>` tags and `.svg` files to PNG
- **🎨 Content Optimization**: Improved Windows compatibility and Halo renderer compatibility
- **⚡ Smart Slug Generation**: Guaranteed unique slugs with timestamp suffixes
- **🔄 Dual Conversion Engine**: Inkscape (preferred) or cairosvg (fallback)
- **📊 Detailed Logging**: Clear status messages for every step

## Prerequisites

### Required
- Python 3.7+
- Halo 2.x instance
- Halo access token with **ALL** following permissions:
  - `posts:create` - create new posts
  - `posts:write` - edit/publish posts  
  - **`attachments:create`** - upload images (VERY IMPORTANT!)
  
⚠️ **Without `attachments:create`, images will fail to upload and won't display.**

### Optional (for SVG conversion)
- **Inkscape 1.0+** (recommended): https://inkscape.org/release/
- **OR cairosvg + cairo**: `pip install cairosvg` + system cairo library

For Windows cairosvg, install GTK3 runtime: see `docs/CAIRO_SETUP.md`.

## Quick Start

### 1. Environment Setup

```bash
export HALO_BASE_URL="https://your-halo-site.com"
export HALO_TOKEN="your-access-token"
```

To generate a token in Halo:
1. Log into Halo admin panel
2. Click avatar → **Access Tokens**
3. Generate new token with appropriate permissions

### 2. Basic Publish

```bash
python ./scripts/run_pipeline.py \
  --article "path/to/article.md" \
  --publish-status PUBLISHED
```

### 3. With Images and Cover

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --publish-status PUBLISHED
```

### 4. With SVG Support

The tool automatically handles:
- Embedded `<svg>` tags in Markdown
- External `.svg` image files
- SVG cover images

All SVGs are converted to PNG and uploaded to Halo.

```bash
# Works with articles containing SVG graphics
python ./scripts/run_pipeline.py \
  --article "article-with-svg.md" \
  --images-dir "./images" \
  --cover "cover.svg" \
  --publish-status PUBLISHED
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--article` | Yes | Path to the Markdown file |
| `--images-dir` | No | Directory containing images referenced in the article |
| `--cover` | No | Cover image file path (supports SVG) |
| `--publish-status` | No | `PUBLISHED` or `DRAFT` (default: PUBLISHED) |
| `--categories` | No | Comma-separated list of categories (e.g., "技术,教程") |
| `--tags` | No | Comma-separated list of tags (e.g., "Manim,Python") |
| `--template` | No | Article template name |
| `--halo-base-url` | No | Override `HALO_BASE_URL` environment variable |
| `--halo-token` | No | Override `HALO_TOKEN` environment variable |

## How It Works

### Publishing Pipeline

1. **Read Article** - Load Markdown content from file
2. **SVG Processing** (if no converter error):
   - Extract embedded `<svg>` tags
   - Convert to PNG using cairosvg (requires cairo) or inkscape
   - Upload PNG to Halo
   - Replace `<svg>` with `![](url)` in Markdown
3. **Process Cover**:
   - If SVG → convert → upload → use PNG URL
   - If other → upload directly
4. **Image Directory**:
   - Replace all local image references `![alt](path)`
   - `.svg` files are converted before upload
   - Upload to Halo and replace with remote URLs
5. **Content Optimization**:
   - Clean up potential rendering issues
   - Normalize whitespace
   - Ensure Halo compatibility
6. **Create Post**:
   - Generate slug from title (ASCII-only, with Chinese pinyin)
   - Build payload with content and metadata
   - POST to Halo Console API
7. **Publish** (if status is PUBLISHED):
   - Call separate publish endpoint to ensure content is live

### GIF: Workflow Overview

```
article.md + images-dir/
     ↓
[Read & Parse]
     ↓
[SVG Processing] ← Inkscape/cairo
     ↓
[Image Upload] → Halo
     ↓
[Content Optimize]
     ↓
[API Call] → Halo 2.x
     ↓
✅ Published
```

## SVG Conversion Details

### Priority Order
1. **Inkscape** (if installed) - Best quality, full SVG spec support
2. **cairosvg** (if cairo available) - Good quality, pure Python
3. **Skip** - If neither available, logs warning and leaves SVG as-is

### Installation

```bash
# For cairosvg only (needs cairo)
pip install cairosvg

# For Inkscape (recommended)
# Download from: https://inkscape.org/release/inkscape-1.4/
# Install normally, it will be auto-detected
```

### Testing Conversion

```bash
# Check if inkscape is available
inkscape --version

# Check if cairosvg works (with cairo)
python -c "import cairosvg; cairosvg.svg2png(bytestring=b'<svg></svg>', write_to='test.png')"
```

## Content Optimization

The tool automatically optimizes Markdown for Halo:

- **Remove stray SVG tags** (if conversion failed)
- **Normalize line breaks** (max 2 consecutive newlines)
- **Preserve all formatting** (bold, italic, code, tables)
- **UTF-8 safe** for Windows consoles

## Slug Generation

- ASCII-only (a-z, 0-9, hyphens)
- Chinese characters → pinyin approximation
- Timestamp suffix ensures uniqueness
- Examples:
  - `我用代码把数学公式变成了动画` → `wo-yong-dai-ma-ba-shu-xue-gong-shi-bian-cheng-1709211234`
  - `Manim 教程` → `manim-jiao-cheng-1709211234`

## API Details

This tool uses Halo 2.x Console API:

- **Create Post**: `POST /apis/api.console.halo.run/v1alpha1/posts`
- **Upload Attachment**: `POST /apis/content.halo.run/v1alpha1/attachments`
- **Publish Post**: `POST /apis/api.console.halo.run/v1alpha1/posts/{name}/publish`

Payload structure follows Halo 2.x PostRequest schema with required fields:
```json
{
  "content": {
    "raw": "markdown content",
    "rawType": "markdown"
  },
  "post": {
    "spec": {
      "title": "...",
      "slug": "...",
      "publish": true,
      "excerpt": {"raw": "...", "autoGenerate": false}
    },
    "metadata": {
      "name": "slug"
    }
  }
}
```

## Troubleshooting

### 400 Bad Request - Duplicate Name
- **Cause**: Slug already exists
- **Fix**: Automatically adds timestamp to ensure uniqueness. If still failing, check for existing posts with similar titles.

### SVG Conversion Fails
- **Symptoms**: "no library called 'cairo-2'" or "cannot find inkscape"
- **Fix**:
  - Option 1: Install Inkscape (https://inkscape.org/)
  - Option 2: Install GTK3/cairo runtime for cairosvg
  - Option 3: Manually convert SVG to PNG and provide via `--images-dir`

### 400 Bad Request - Schema Violation
- **Cause**: Missing required fields or invalid data
- **Fix**: Ensure `excerpt.autoGenerate` is present. Check categories/tags exist in Halo.

### Preview Shows No Content
- **Cause**: `publish: true` not set or content not released
- **Fix**: Tool calls publish endpoint automatically for PUBLISHED status. Check Halo backend logs.

### Images Not Uploading
- **Cause**: File not found or permission denied
- **Fix**: Ensure `images-dir` exists and contains valid image files. Check file permissions.

## Project Structure

```
halo-auto-article-publisher/
├── scripts/
│   ├── run_pipeline.py      # Main entry point
│   ├── halo_client.py       # Halo API client
│   ├── common.py            # Utilities (slug, title parse)
│   └── image_processor.py   # SVG→PNG conversion
├── agents/                  # Optional: custom agents
├── output/                  # Generated output
├── references/              # Reference materials
├── SKILL.md                 # This file
├── README.md                # Detailed documentation
├── CHANGELOG_v2.md          # Version history
└── .gitignore
```

## Development

### Testing Locally

Always test with DRAFT first:

```bash
python scripts/run_pipeline.py \
  --article "test-article.md" \
  --publish-status DRAFT
```

Verify in Halo admin before publishing live.

### Adding New Features

1. **New CLI arguments**: Add to `argparse` in `run_pipeline.py`
2. **New image types**: Extend `ImageProcessor` class
3. **Custom slug rules**: Modify `generate_slug()` in `common.py`
4. **Content filters**: Add to `optimize_content_for_halo()`

## Migration from v1.x

If you're using the old version:

1. **Install optional dependencies** (for SVG):
   ```bash
   pip install cairosvg
   # or install Inkscape
   ```

2. **No breaking changes** - all existing commands work unchanged

3. **New capabilities automatically enabled**:
   - SVG conversion (if dependencies available)
   - Improved slug uniqueness
   - Better Windows compatibility

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit Pull Request with detailed description

## License

MIT License. See LICENSE file for details.

## Support

- **Issues**: https://github.com/gongxings/halo-auto-article-publisher/issues
- **Halo Documentation**: https://docs.halo.run/
- **Halo Community**: https://halo.run/community/

---

**Happy Publishing! 🚀**
