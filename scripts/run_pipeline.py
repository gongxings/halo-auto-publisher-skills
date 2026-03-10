from __future__ import annotations

import argparse
import hashlib
import mimetypes
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests


def _load_dotenv():
    """从脚本目录（或其父目录）查找 .env 文件并加载，已存在的环境变量不会被覆盖。"""
    search_dirs = [
        Path(__file__).parent,          # scripts/
        Path(__file__).parent.parent,   # 项目根目录
    ]
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
            break  # 找到第一个就停止


_load_dotenv()

from common import assert_env, get_markdown_title, generate_slug, sanitize_summary
from halo_client import publish_post, publish_post_to_live, upload_attachment
from image_processor import ImageProcessor


def _is_real_image_url(url: str) -> bool:
    """
    判断远程 URL 是否是需要下载的真实图片（而非徽章、SVG 图表等）。
    返回 True 表示应该下载并上传到 Halo。
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()

    # 跳过：徽章/图表类域名
    skip_domains = [
        "shields.io",
        "img.shields.io",
        "star-history.com",
        "api.star-history.com",
        "badgen.net",
        "badge.fury.io",
        "travis-ci.org",
        "travis-ci.com",
        "codecov.io",
        "coveralls.io",
    ]
    for domain in skip_domains:
        if netloc == domain or netloc.endswith("." + domain):
            return False

    # 跳过：URL 路径含有徽章关键词
    skip_keywords = ["badge", "shield", "workflow/badge", "actions/workflows"]
    for kw in skip_keywords:
        if kw in path:
            return False

    # 跳过：SVG 文件
    if path.endswith(".svg"):
        return False

    # 跳过：GitHub camo 代理（通常代理的是外部徽章）
    if netloc == "camo.githubusercontent.com":
        return False

    # 满足以下条件之一视为真实图片：
    # 1. 常见图片扩展名
    real_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".avif"}
    suffix = Path(path.split("?")[0]).suffix.lower()
    if suffix in real_exts:
        return True

    # 2. GitHub 用户上传的附件（user-attachments / assets）
    if "user-attachments" in url or "/assets/" in path:
        return True

    # 3. GitHub raw 内容
    if netloc == "raw.githubusercontent.com":
        return True

    # 4. 私有 GitHub 用户图片（private-user-images）
    if "private-user-images.githubusercontent.com" in netloc:
        return True

    return False


def fetch_and_upload_remote_images(markdown: str, work_dir: Path, upload_func) -> str:
    """
    扫描 Markdown 中所有远程图片引用（https://...），
    对符合条件的真实图片：下载 → 上传到 Halo → 替换为 Halo URL。
    下载失败时打印警告并保留原始 URL，不中断流程。
    """
    pattern = r'!\[([^\]]*)\]\((https?://[^)]+)\)'
    matches = re.findall(pattern, markdown)

    if not matches:
        return markdown

    # 去重：同一 URL 只下载一次
    unique_urls = list(dict.fromkeys(url for _, url in matches))
    real_urls = [u for u in unique_urls if _is_real_image_url(u)]

    if not real_urls:
        print("[*] 未发现需要抓取的远程图片（徽章/SVG 已跳过）")
        return markdown

    print(f"[*] 发现 {len(real_urls)} 张远程图片，开始下载并上传...")

    url_map: dict[str, str] = {}  # 原始 URL → Halo URL

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for url in real_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            # 推断文件扩展名
            content_type = resp.headers.get("Content-Type", "")
            ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ""
            # mimetypes 在 Windows 上可能返回 .jpe，统一修正
            ext_map = {".jpe": ".jpg", ".jpeg": ".jpg", "": ".png"}
            ext = ext_map.get(ext, ext)

            # 也可从 URL 路径推断
            if not ext or ext not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
                url_path = urlparse(url).path
                url_ext = Path(url_path.split("?")[0]).suffix.lower()
                if url_ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
                    ext = url_ext
                else:
                    ext = ".png"  # 兜底

            # 以 URL hash 命名，避免重复
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            local_path = work_dir / f"remote_{url_hash}{ext}"
            local_path.write_bytes(resp.content)

            halo_url = upload_func(str(local_path))
            url_map[url] = halo_url
            print(f"[+] 远程图片已上传: {url[:60]}{'...' if len(url) > 60 else ''}")

        except Exception as e:
            print(f"[!] 远程图片下载/上传失败（保留原URL）: {url[:60]}{'...' if len(url) > 60 else ''}\n    原因: {e}")

    if not url_map:
        return markdown

    # 替换 Markdown 中所有匹配到的 URL
    def repl(match: re.Match) -> str:
        alt = match.group(1)
        url = match.group(2)
        if url in url_map:
            return f"![{alt}]({url_map[url]})"
        return match.group(0)

    return re.sub(pattern, repl, markdown)


def optimize_content_for_halo(markdown: str, skip_svg: bool = False) -> str:
    """
    优化Markdown内容，使其更适合Halo渲染器
    
    - 处理Windows编码兼容性
    - 清理可能引起问题的HTML标签（除非skip_svg）
    - 确保标题层级合理
    - 移除调试信息
    """
    lines = markdown.split('\n')
    result = []
    
    for i, line in enumerate(lines):
        # 处理SVG标签（除非跳过）
        if not skip_svg and '<svg' in line.lower():
            print(f"[!] 发现未处理的内嵌SVG（第{i+1}行），建议使用--images-dir参数")
            continue
            
        # 移除可能的调试注释
        if line.strip().startswith('<!--') and 'DEBUG' in line:
            continue
            
        result.append(line)
    
    optimized = '\n'.join(result)
    
    # 规范化空行
    optimized = re.sub(r'\n{3,}', '\n\n', optimized)
    
    return optimized.strip()


def replace_image_urls(markdown: str, images_dir: Path, upload_func) -> str:
    """将 Markdown 中的本地图片引用替换为已上传的远程 URL。"""
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def repl(match):
        alt = match.group(1)
        src = match.group(2)
        # 跳过已经是 URL 的图片
        if src.startswith('http://') or src.startswith('https://'):
            return match.group(0)
        # 处理.svg文件：转换为PNG再上传
        if src.lower().endswith('.svg'):
            # 构建完整路径
            local_path = images_dir / src if not Path(src).is_absolute() else Path(src)
            if local_path.exists() and local_path.is_file():
                # 临时PNG路径
                png_path = local_path.with_suffix('.png')
                # 转换SVG到PNG
                if ImageProcessor.convert_svg_to_png(local_path, png_path):
                    try:
                        remote_url = upload_func(str(png_path))
                        return f'![{alt}]({remote_url})'
                    except Exception as e:
                        print(f"警告：上传转换后的图片失败 {png_path}: {e}")
                        return match.group(0)
                else:
                    print(f"警告：SVG转换失败，跳过: {local_path}")
                    return match.group(0)
            else:
                return match.group(0)
        # 普通图片文件
        local_path = images_dir / src if not Path(src).is_absolute() else Path(src)
        if local_path.exists() and local_path.is_file():
            try:
                remote_url = upload_func(str(local_path))
                return f'![{alt}]({remote_url})'
            except Exception as e:
                print(f"警告：上传图片失败 {local_path}: {e}")
                return match.group(0)
        else:
            return match.group(0)
    
    return re.sub(pattern, repl, markdown)


def publish_article(
    article_path: str,
    images_dir: str = "",
    cover_image: str = "",
    publish_status: str = "PUBLISHED",
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    template: str = "",
    skip_svg: bool = False,  # 新增参数
) -> dict:
    article_path_obj = Path(article_path)
    if not article_path_obj.exists():
        raise FileNotFoundError(f"未找到文章文件：{article_path}")
    article_md = article_path_obj.read_text(encoding="utf-8")
    
    # 创建临时工作目录用于SVG转换
    with tempfile.TemporaryDirectory(prefix="halo_publish_") as temp_dir:
        work_dir = Path(temp_dir)
        
        cover_url = ""
        
        # 1. 处理封面（如果是SVG）
        if cover_image:
            cover_path = Path(cover_image)
            if cover_path.exists():
                if cover_path.suffix.lower() == '.svg':
                    cover_png = work_dir / "cover.png"
                    if ImageProcessor.convert_svg_to_png(cover_path, cover_png):
                        cover_url = upload_attachment(str(cover_png))
                        print("[+] 封面SVG已转换并上传")
                    else:
                        print("[!] 封面SVG转换失败，使用原始文件")
                        cover_url = upload_attachment(cover_image)
                else:
                    cover_url = upload_attachment(cover_image)
        
        # 2. 处理文章中的内嵌SVG标签
        print("[*] 扫描并处理内嵌SVG...")
        article_md = ImageProcessor.replace_svg_with_images(
            article_md, work_dir, upload_attachment
        )
        
        # 3. 抓取并上传远程图片（真实截图/预览图，跳过徽章/SVG图表）
        print("[*] 扫描并下载远程图片...")
        article_md = fetch_and_upload_remote_images(article_md, work_dir, upload_attachment)
        
        # 4. 优化内容
        article_md = optimize_content_for_halo(article_md, skip_svg=False)
        
        # 5. 处理外部图片目录（包括嵌入的图片引用）
        if images_dir:
            images_dir_path = Path(images_dir)
            if images_dir_path.exists():
                print(f"[+] 处理图片目录: {images_dir}")
                article_md = replace_image_urls(article_md, images_dir_path, upload_attachment)
        
        title = get_markdown_title(article_path_obj)
        # 去掉内容中的一级标题行，避免 Halo 渲染时标题重复显示
        article_md = re.sub(r'^#\s+.+\n?', '', article_md, count=1).lstrip('\n')
        summary = sanitize_summary(article_md, max_len=160)
        
        # 发布文章
        try:
            resp = publish_post(
                title=title,
                content_markdown=article_md,
                summary=summary,
                cover_url=cover_url,
                publish_status=publish_status,
                categories=categories,
                tags=tags,
                template=template,
            )
        except Exception as e:
            print(f"Error: {e}")
            # 尝试获取响应详情
            if hasattr(e, 'response'):
                try:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response body: {e.response.text}")
                except:
                    pass
            raise

        # If we need to ensure publication (Halo 2.x sometimes needs explicit publish call)
        # Note: resp contains the post with metadata.name
        post_name = resp.get("post", {}).get("metadata", {}).get("name")
        if publish_status.upper() == "PUBLISHED" and post_name:
            try:
                # Call publish endpoint to ensure content is released
                publish_post_to_live(post_name)
            except Exception as e:
                print(f"[!] 警告：单独发布步骤失败（可忽略）: {e}")

        return {
            "title": title,
            "publishStatus": publish_status,
            "coverUrl": cover_url,
            "categories": categories or [],
            "tags": tags or [],
            "haloResponse": resp,
        }


def main():
    parser = argparse.ArgumentParser(description="发布 Markdown 文章到 Halo。")
    parser.add_argument("--article", required=True, help="文章文件路径")
    parser.add_argument("--images-dir", default="", help="文章引用的图片目录（可选）")
    parser.add_argument("--cover", default="", help="封面图片路径（可选）")
    parser.add_argument("--publish-status", choices=["PUBLISHED", "DRAFT"], default="PUBLISHED")
    parser.add_argument("--categories", default="", help="分类列表，逗号分隔（可选，如：'技术,教程'）")
    parser.add_argument("--tags", default="", help="标签列表，逗号分隔（可选，如：'Manim,数学动画'）")
    parser.add_argument("--template", default="", help="文章模板名称（可选）")
    parser.add_argument("--halo-base-url", default="", help="Halo 地址（覆盖环境变量）")
    parser.add_argument("--halo-token", default="", help="Halo 令牌（覆盖环境变量）")
    args = parser.parse_args()

    # 处理分类和标签
    categories = [c.strip() for c in args.categories.split(",")] if args.categories else None
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

    # 覆盖环境变量
    if args.halo_base_url:
        os.environ["HALO_BASE_URL"] = args.halo_base_url
    if args.halo_token:
        os.environ["HALO_TOKEN"] = args.halo_token

    # 检查必要环境变量
    assert_env("HALO_BASE_URL")
    assert_env("HALO_TOKEN")

    result = publish_article(
        article_path=args.article,
        images_dir=args.images_dir,
        cover_image=args.cover,
        publish_status=args.publish_status,
        categories=categories,
        tags=tags,
        template=args.template,
    )
    # Print result safely (avoid Windows console encoding issues)
    import json
    print("Article published successfully!")
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Status: {result.get('publishStatus', 'N/A')}")
    if result.get('coverUrl'):
        print(f"Cover: {result['coverUrl']}")


if __name__ == "__main__":
    main()
