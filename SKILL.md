---
name: halo-article-publisher
description: Publish a Markdown article to Halo blog with full SVG support, automatic remote image fetching, content optimization, and automatic image handling. Use when user provides a ready article and wants to upload it to Halo: fetch and upload remote images from GitHub/web, upload local images (including SVG→PNG conversion), set cover, and publish or save as draft. Always publishes with rawType=markdown so Halo renders natively.
version: 2.2.0
tags:
  - publishing
  - blog
  - halo
  - markdown
  - images
  - svg
  - content-optimization
  - remote-images
author: gongxings
---

# Halo Article Publisher v2.1

Publish an existing Markdown article to Halo blog platform with full Halo 2.x support, automatic SVG conversion, remote image fetching, and content optimization.

## ✨ New in v2.1

- **🌐 Remote Image Fetching**: Automatically download real images (screenshots, previews) from GitHub and other URLs, upload to Halo, and replace in Markdown — badges and SVG charts are skipped
- **📝 Native Markdown Publishing**: Content is always submitted as `rawType: markdown`, Halo renders it natively without format conversion

## ✨ Features from v2.0

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

## How to Write the Article (AI Instructions)

When the user asks you to **generate an article from a GitHub project** (or any web source) and publish it, follow these rules strictly:

### Step 1 — Research the project

Fetch the project's README, CHANGELOG, and any relevant pages. Collect:
- Project description and key features
- All **real image URLs** present in the README (screenshots, demo GIFs, preview images)
- Tech stack, quick start instructions, roadmap

### Step 2 — Write the Markdown article

Write a high-quality Chinese article (unless user specifies otherwise). Structure:

```
开篇简介（1-2段，交代项目背景和价值）
注意：不要在文章内容中写一级标题（# 标题），Halo 会自动显示文章标题，写了会重复。

## 项目截图          ← 第一个有图片的位置，放项目主截图
![项目截图](原始URL)

## 核心特性
...

## 技术栈
...（可用表格）

## 功能演示 / 界面预览   ← 如果README有更多截图，在此插入
![功能演示](原始URL)

## 快速上手
...（代码块）

## 总结
...
```

> **注意**：文章从正文开始，**不要**写 `# 文章标题` 这样的一级标题行。Halo 渲染文章时会在页面顶部自动显示标题，如果内容里还有一级标题会导致重复。二级标题（`##`）及以下正常使用。

### Step 3 — Image embedding rules (CRITICAL)

**You MUST embed images from the project into the article using standard Markdown syntax.**

Rules:
1. **Scan the README/project pages** for all real image URLs (screenshots, demo GIFs, preview images)
2. **Embed them using**: `![描述性alt文字](原始完整URL)`
3. **Place images at logical positions** in the article — after introducing a feature, after a section header, or as a dedicated "项目截图" / "界面预览" section
4. **Include at least 1 image** if the project has any screenshots. If the project has 3+ screenshots, include all of them at appropriate positions
5. **Use the original remote URL** as-is in the Markdown. The publisher pipeline will automatically download and re-upload them to Halo
6. **Do NOT skip images** just because the URL looks long or complex (GitHub user-attachments URLs are valid)
7. **Do NOT use placeholder text** like `[图片]` or `[截图]` — use real URLs or omit entirely

**Good example:**
```markdown
## 项目截图

下面是 Magic Resume 的编辑器界面，支持实时预览和多套主题：

![Magic Resume 编辑器界面](https://github.com/user-attachments/assets/4667e49a-7bf2-4379-9390-725e42799dc7)

## 核心特性
...
```

**Bad example (do NOT do this):**
```markdown
## 项目截图

（项目截图）

## 核心特性
```

### Step 4 — Save and publish

Save the article as a `.md` file, then run the publisher pipeline. The pipeline will:
- Download all `![alt](https://...)` image URLs and upload them to Halo attachments
- Replace original URLs with Halo-hosted URLs in the final post
- Publish with `rawType: markdown`



**Recommended: use a `.env` file** (no need to pass credentials on every run).

Create a `.env` file in the skill root directory (next to `scripts/`):

```ini
# halo-article-publisher/.env
HALO_BASE_URL=https://your-halo-site.com
HALO_TOKEN=your-access-token

# Optional: attachment upload policy (default: default-policy)
# HALO_ATTACHMENT_POLICY=default-policy
```

The script automatically loads `.env` on startup — values already set in the environment take priority, so you can still override per-run via `export` or `--halo-base-url` / `--halo-token` flags.

Alternatively, set environment variables directly:

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
2. **SVG Processing** (if converter available):
   - Extract embedded `<svg>` tags
   - Convert to PNG using Inkscape or cairosvg
   - Upload PNG to Halo
   - Replace `<svg>` with `![](url)` in Markdown
3. **Remote Image Fetching** (new in v2.1):
   - Scan all `![alt](https://...)` references in Markdown
   - Skip badges (shields.io, badgen.net, etc.), SVG charts, and camo proxies
   - Download real images (screenshots, previews, raw GitHub assets)
   - Upload to Halo and replace URLs in Markdown
   - Failed downloads are warned and original URLs preserved
4. **Process Cover**:
   - If SVG → convert → upload → use PNG URL
   - If other → upload directly
5. **Image Directory**:
   - Replace all local image references `![alt](path)`
   - `.svg` files are converted before upload
   - Upload to Halo and replace with remote URLs
6. **Content Optimization**:
   - Clean up potential rendering issues
   - Normalize whitespace
   - Ensure Halo compatibility
7. **Create Post** (rawType: markdown):
   - Generate slug from title (ASCII-only, with Chinese pinyin)
   - Build payload with `rawType: "markdown"` — no HTML conversion
   - POST to Halo Console API
8. **Publish** (if status is PUBLISHED):
   - Call separate publish endpoint to ensure content is live

### Workflow Overview

```
article.md + images-dir/
     ↓
[Read & Parse]
     ↓
[SVG Processing] ← Inkscape/cairo
     ↓
[Remote Image Fetch] ← download & upload real images  ← NEW in v2.1
     ↓
[Local Image Upload] ← --images-dir
     ↓
[Content Optimize]
     ↓
[API Call] rawType: markdown → Halo 2.x
     ↓
✅ Published
```

### Remote Image Fetching (v2.1)

The tool automatically identifies and fetches "real" images from remote URLs:

**Downloaded** (uploaded to Halo):
- GitHub user-attachments and `/assets/` paths
- `raw.githubusercontent.com` content
- URLs with image extensions (`.png`, `.jpg`, `.gif`, `.webp`, etc.)

**Skipped** (kept as-is):
- `shields.io`, `badgen.net` and similar badge services
- `star-history.com` and other chart services
- `camo.githubusercontent.com` (GitHub badge proxy)
- Any URL containing `badge` or `shield` in the path
- `.svg` URLs

Failed downloads print a warning and preserve the original URL — publishing continues normally.

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

### Remote Image Download Fails
- **Symptoms**: `[!] 远程图片下载/上传失败` in output
- **Cause**: Network timeout, 403 Forbidden (expired token in URL), or unsupported host
- **Fix**: Original URL is preserved automatically. For private GitHub images with expired tokens, regenerate the article with fresh URLs.

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
