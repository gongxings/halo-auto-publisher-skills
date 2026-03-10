from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

from common import assert_env, generate_slug, with_retry


def _halo_headers() -> dict[str, str]:
    token = assert_env("HALO_TOKEN")
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _halo_url(path: str) -> str:
    base = assert_env("HALO_BASE_URL").rstrip("/")
    if path.startswith("http"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def upload_attachment(file_path: str) -> str:
    """
    上传附件到 Halo。
    优先使用 console API（/apis/api.console.halo.run/v1alpha1/attachments/upload），
    需要携带 policyName 参数，URL 从响应的 metadata.annotations 中提取。
    若失败则回退到旧端点。
    """
    base = assert_env("HALO_BASE_URL").rstrip("/")
    policy_name = os.getenv("HALO_ATTACHMENT_POLICY", "default-policy")
    group_name = os.getenv("HALO_ATTACHMENT_GROUP", "")

    # 优先用 console upload 端点
    console_endpoint = "/apis/api.console.halo.run/v1alpha1/attachments/upload"
    fallback_endpoint = os.getenv("HALO_UPLOAD_ENDPOINT", "/apis/content.halo.run/v1alpha1/attachments")

    def _do_console() -> str:
        url = base + console_endpoint
        with open(file_path, "rb") as fp:
            import mimetypes as _mt
            mime = _mt.guess_type(file_path)[0] or "application/octet-stream"
            resp = requests.post(
                url,
                headers=_halo_headers(),
                files={"file": (Path(file_path).name, fp, mime)},
                data={"policyName": policy_name, "groupName": group_name},
                timeout=60,
            )
        resp.raise_for_status()
        data = resp.json()
        # 从 metadata.annotations 取相对 URI，再拼 base URL
        annotations = (data.get("metadata") or {}).get("annotations") or {}
        uri = annotations.get("storage.halo.run/uri", "")
        if uri:
            return base + uri
        # 兜底：尝试其他字段
        for candidate in [
            data.get("url"),
            data.get("permalink"),
            (data.get("status") or {}).get("permalink"),
            (data.get("spec") or {}).get("url"),
        ]:
            if candidate:
                return candidate
        raise RuntimeError(f"Cannot extract URL from upload response: {data}")

    def _do_fallback() -> str:
        url = base + fallback_endpoint
        with open(file_path, "rb") as fp:
            resp = requests.post(
                url,
                headers=_halo_headers(),
                files={"file": (Path(file_path).name, fp)},
                timeout=60,
            )
        resp.raise_for_status()
        data = resp.json()
        for candidate in [
            data.get("url"),
            data.get("permalink"),
            (data.get("status") or {}).get("permalink"),
            (data.get("spec") or {}).get("url"),
            (data.get("data") or {}).get("url"),
        ]:
            if candidate:
                return candidate
        raise RuntimeError("Halo upload response did not include attachment URL")

    # 先尝试 console 端点，失败则回退
    try:
        return with_retry(_do_console)
    except Exception as e:
        print(f"[!] console 上传端点失败，尝试回退端点: {e}")
        return with_retry(_do_fallback)


def publish_post(
    title: str,
    content_markdown: str,
    summary: str = "",
    cover_url: str = "",
    publish_status: str = "PUBLISHED",
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    template: str = "",
) -> dict:
    """
    Publish a post to Halo 2.x.
    
    Args:
        title: Post title
        content_markdown: Markdown content
        summary: Brief summary/excerpt
        cover_url: Cover image URL (already uploaded)
        publish_status: "PUBLISHED" or "DRAFT"
        categories: List of category names (must exist in Halo)
        tags: List of tag names (will be created if not exists)
        template: Custom template name (optional)
    
    Returns:
        dict: Halo API response
    """
    # Halo 2.x uses Console API endpoint
    endpoint = os.getenv("HALO_POST_ENDPOINT", "/apis/api.console.halo.run/v1alpha1/posts")
    url = _halo_url(endpoint)

    published = publish_status.upper() == "PUBLISHED"

    # Generate English-only slug from title
    import time
    slug = generate_slug(title)
    # Always add timestamp suffix for guaranteed uniqueness
    slug = f"{slug}-{int(time.time())}"

    # Build spec with required fields
    spec: dict = {
        "title": title,
        "slug": slug,
        "allowComment": True,
        "deleted": False,
        "excerpt": {
            "raw": summary,
            "autoGenerate": False if summary else True
        },
        "pinned": False,
        "priority": 0,
        "publish": published,
        "visible": "PUBLIC"
    }
    
    # Add optional fields
    if cover_url:
        spec["cover"] = cover_url
    
    if template:
        spec["template"] = template
    
    if categories:
        spec["categories"] = categories
    
    if tags:
        spec["tags"] = tags

    # Build payload according to Halo 2.x PostRequest schema
    payload = {
        "content": {
            "raw": content_markdown,
            "rawType": "markdown"
        },
        "post": {
            "spec": spec,
            "metadata": {
                "name": slug
            }
        }
    }

    def _do() -> dict:
        headers = _halo_headers()
        headers["Content-Type"] = "application/json"
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result

    return with_retry(_do)


def publish_post_to_live(post_name: str) -> dict:
    """
    Publish a draft post to live (create release snapshot).
    This is sometimes needed for Halo 2.x to make content visible.
    
    Args:
        post_name: The metadata.name of the post
        
    Returns:
        dict: Halo API response
    """
    endpoint = f"/apis/api.console.halo.run/v1alpha1/posts/{post_name}/publish"
    url = _halo_url(endpoint)

    def _do() -> dict:
        headers = _halo_headers()
        headers["Content-Type"] = "application/json"
        # Empty payload for publish endpoint
        payload = {}
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

    return with_retry(_do)
