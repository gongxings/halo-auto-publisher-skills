# Halo Auto Article Publisher

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Halo](https://img.shields.io/badge/Halo-2.x-orange.svg)](https://www.halo.run/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automatically publish Markdown articles to Halo blog platform with full Halo 2.x support.

## Features

- ✅ **Full Halo 2.x Support** - Works with Halo 2.x Console API
- ✅ **Category & Tag Support** - Assign categories and tags to posts
- ✅ **Image Upload** - Automatically upload local images and update Markdown references
- ✅ **Cover Image** - Set custom cover images for articles
- ✅ **English Slug Generation** - Auto-generate URL-friendly slugs from titles (supports Chinese → pinyin)
- ✅ **Draft/Publish** - Save as draft or publish immediately
- ✅ **Template Support** - Use custom Halo templates
- ✅ **Batch Processing** - Process multiple articles with different categories/tags
- ✅ **Retry Logic** - Automatic retry on transient failures

## Installation

### Prerequisites

- Python 3.7+
- Halo 2.x instance
- Halo access token with `posts:create` and `posts:write` permissions

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/gongxings/halo-auto-article-publisher.git
cd halo-auto-article-publisher
```

2. **Install dependencies**

```bash
pip install requests
```

3. **Configure environment variables**

```bash
export HALO_BASE_URL="https://your-halo-site.com"  # Your Halo site URL
export HALO_TOKEN="your-access-token"              # Halo API access token
```

To generate a token in Halo:
1. Log into Halo admin panel
2. Click avatar → **Access Tokens**
3. Generate new token with appropriate permissions

## Usage

### Basic Publish

```bash
python ./scripts/run_pipeline.py \
  --article "path/to/article.md" \
  --publish-status PUBLISHED
```

### With Images and Cover

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --publish-status PUBLISHED
```

### With Categories and Tags

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --categories "技术,Python,教程" \
  --tags "Manim,数学动画,编程" \
  --template "default" \
  --publish-status PUBLISHED
```

### Save as Draft

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --publish-status DRAFT
```

### Override Environment

```bash
python ./scripts/run_pipeline.py \
  --article "article.md" \
  --halo-base-url "https://staging.halo.com" \
  --halo-token "temp-token-123" \
  --publish-status PUBLISHED
```

## Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--article` | Yes | Path to the Markdown file |
| `--images-dir` | No | Directory containing images referenced in the article |
| `--cover` | No | Path to cover image file |
| `--publish-status` | No | `PUBLISHED` or `DRAFT` (default: PUBLISHED) |
| `--categories` | No | Comma-separated list of categories (e.g., "技术,教程") |
| `--tags` | No | Comma-separated list of tags (e.g., "Manim,Python") |
| `--template` | No | Custom template name |
| `--halo-base-url` | No | Override HALO_BASE_URL environment variable |
| `--halo-token` | No | Override HALO_TOKEN environment variable |

## How It Works

1. **Parse Markdown** - Extracts title from the first `# heading`
2. **Process Images** - Uploads local images to Halo and updates Markdown references
3. **Upload Cover** - Uploads cover image if provided
4. **Generate Slug** - Creates an English URL slug from the title (with Chinese → pinyin support)
5. **Build Payload** - Constructs Halo 2.x compatible payload with content and metadata
6. **Publish** - Creates post and calls publish endpoint to ensure content is visible

### Slug Generation Examples

- "我用代码把数学公式变成了动画" → `wo-yong-dai-ma-ba-shu-xue-gong-shi-bian-cheng`
- "Manim 教程" → `manim-jiao-cheng`
- "Python 入门指南" → `python-ru-men-zhi-nan`

The tool includes a built-in Chinese character → pinyin mapping for common characters. For more accurate transliteration, you can extend the mapping in `common.py`.

## API Details

This tool uses Halo 2.x Console API:

- **Create Post**: `POST /apis/api.console.halo.run/v1alpha1/posts`
- **Upload Attachment**: `POST /apis/content.halo.run/v1alpha1/attachments`
- **Publish Post**: `POST /apis/api.console.halo.run/v1alpha1/posts/{name}/publish`

**Note**: This tool is designed for Halo 2.x and is NOT compatible with Halo 1.x.

## Installing in OpenCode / Codex

### OpenCode AI

1. **Locate your OpenCode skills directory**
   - Typically: `~/.opencode/skills/`
   - Or: Check OpenCode settings → Skills → Skill Directory

2. **Copy or symlink the skill**
   ```bash
   # Copy
   cp -r halo-auto-article-publisher ~/.opencode/skills/
   
   # Or symlink (recommended for development)
   ln -s /path/to/halo-auto-article-publisher ~/.opencode/skills/
   ```

3. **Restart OpenCode**
   - The skill will be automatically loaded

4. **Use in OpenCode**
   - The skill is now available as `halo-auto-article-publisher`
   - Invoke by asking OpenCode to publish an article to Halo

### Claude Code (Codex)

1. **Locate your Codex skills directory**
   - **macOS/Linux**: `~/.config/claude/skills/`
   - **Windows**: `%APPDATA%\Claude\skills\`

2. **Copy or symlink the skill**
   ```bash
   # macOS/Linux
   ln -s /path/to/halo-auto-article-publisher ~/.config/claude/skills/
   
   # Windows (PowerShell as Administrator)
   mklink /D %APPDATA%\Claude\skills\halo-auto-article-publisher C:\path\to\halo-auto-article-publisher
   ```

3. **Restart Claude Code**
   - The skill will be available immediately

4. **Use in Claude Code**
   - Claude can now use this skill to publish articles to your Halo blog

## Troubleshooting

### 401 Unauthorized
- Check your `HALO_TOKEN` is correct and has `posts:create`/`posts:write` permissions
- Regenerate token in Halo admin panel

### 400 Bad Request - Duplicate Name
- The generated slug already exists
- Try a different title or the tool will add a timestamp suffix automatically

### 400 Bad Request - Schema Violation
- Ensure `excerpt.autoGenerate` field is present
- Check categories/tags exist in Halo
- Title and slug are required

### Preview shows no content
- Verify that `publish: true` is set
- The tool calls the separate publish endpoint to ensure content is released
- Check Halo backend logs for errors

### Images not uploading
- Ensure `images-dir` path exists and contains images
- Check file permissions
- Verify Halo upload endpoint is accessible

## Project Structure

```
halo-auto-article-publisher/
├── scripts/
│   ├── run_pipeline.py      # Main entry point
│   ├── halo_client.py       # Halo API client (Halo 2.x)
│   └── common.py            # Utilities (slug generation, title parsing)
├── agents/                  # Optional: custom agents
├── output/                  # Generated output (if any)
├── references/              # Reference materials
├── SKILL.md                 # Original skill definition
├── README.md                # This file
└── .gitignore
```

## Development

### Testing Locally

```bash
# Always test with DRAFT first
export HALO_BASE_URL="https://your-halo-site.com"
export HALO_TOKEN="your-token"
python scripts/run_pipeline.py \
  --article "test-article.md" \
  --publish-status DRAFT
```

### Adding New Features

1. **New API fields**: Add to `publish_post()` in `scripts/halo_client.py`
2. **New CLI arguments**: Add to `argparse` in `scripts/run_pipeline.py`
3. **Custom slug rules**: Modify `generate_slug()` in `scripts/common.py`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a Pull Request with detailed description

## License

MIT License. See LICENSE file for details.

## Acknowledgments

- Built for Halo 2.x Console API
- Inspired by the need to automate blog publishing
- Tested with Halo 2.22.7

## Support

- **Issues**: https://github.com/gongxings/halo-auto-article-publisher/issues
- **Halo Documentation**: https://docs.halo.run/
- **Halo Community**: https://halo.run/community/

---

**Happy Publishing! 🚀**
