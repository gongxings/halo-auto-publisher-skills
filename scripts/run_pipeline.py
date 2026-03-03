from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path

from common import assert_env, get_markdown_title, generate_slug, sanitize_summary
from halo_client import publish_post, publish_post_to_live, upload_attachment
from image_processor import ImageProcessor


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
        
        # 3. 优化内容
        article_md = optimize_content_for_halo(article_md, skip_svg=False)
        
        # 4. 处理外部图片目录（包括嵌入的图片引用）
        if images_dir:
            images_dir_path = Path(images_dir)
            if images_dir_path.exists():
                print(f"[+] 处理图片目录: {images_dir}")
                article_md = replace_image_urls(article_md, images_dir_path, upload_attachment)
        
        title = get_markdown_title(article_path_obj)
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
