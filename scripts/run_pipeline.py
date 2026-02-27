from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from common import assert_env, get_markdown_title, generate_slug, sanitize_summary
from halo_client import publish_post, publish_post_to_live, upload_attachment


def replace_image_urls(markdown: str, images_dir: Path) -> str:
    """将 Markdown 中的本地图片引用替换为已上传的远程 URL。"""
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

    def repl(match):
        alt = match.group(1)
        src = match.group(2)
        # 跳过已经是 URL 的图片
        if src.startswith('http://') or src.startswith('https://'):
            return match.group(0)
        # 计算本地路径（相对 images_dir 或绝对路径）
        local_path = images_dir / src if not Path(src).is_absolute() else Path(src)
        if local_path.exists() and local_path.is_file():
            try:
                remote_url = upload_attachment(str(local_path))
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
) -> dict:
    article_path_obj = Path(article_path)
    if not article_path_obj.exists():
        raise FileNotFoundError(f"未找到文章文件：{article_path}")
    article_md = article_path_obj.read_text(encoding="utf-8")

    cover_url = ""
    if cover_image and Path(cover_image).exists():
        cover_url = upload_attachment(cover_image)

    # 处理文章中的图片引用
    if images_dir:
        images_dir_path = Path(images_dir)
        if images_dir_path.exists():
            article_md = replace_image_urls(article_md, images_dir_path)

    title = get_markdown_title(article_path_obj)
    summary = sanitize_summary(article_md, max_len=160)

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

    # If we need to ensure publication (Halo 2.x sometimes needs explicit publish call)
    # Note: resp contains the post with metadata.name
    post_name = resp.get("post", {}).get("metadata", {}).get("name")
    if publish_status.upper() == "PUBLISHED" and post_name:
        try:
            # Call publish endpoint to ensure content is released
            publish_post_to_live(post_name)
        except Exception as e:
            print(f"警告：单独发布步骤失败（可忽略）: {e}")

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
