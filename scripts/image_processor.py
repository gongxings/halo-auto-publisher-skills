"""图片处理模块：SVG转PNG、图片上传等"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Optional


class ImageProcessor:
    """图片处理器"""
    
    # 缓存检测结果
    _inkscape_available = None
    _cairosvg_available = None
    
    @staticmethod
    def check_dependencies() -> dict[str, bool]:
        """检查可用的转换工具"""
        return {
            'inkscape': ImageProcessor._check_inkscape(),
            'cairosvg': ImageProcessor._check_cairosvg()
        }
    
    @staticmethod
    def _check_inkscape() -> bool:
        """检查inkscape是否可用"""
        if ImageProcessor._inkscape_available is not None:
            return ImageProcessor._inkscape_available
        try:
            result = subprocess.run(
                ['inkscape', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            ImageProcessor._inkscape_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            ImageProcessor._inkscape_available = False
        return ImageProcessor._inkscape_available
    
    @staticmethod
    def _check_cairosvg() -> bool:
        """检查cairosvg是否可用（需要cairo）"""
        if ImageProcessor._cairosvg_available is not None:
            return ImageProcessor._cairosvg_available
        try:
            import cairosvg
            import io
            output = io.BytesIO()
            cairosvg.svg2png(bytestring=b'<svg width="1" height="1"></svg>', write_to=output)
            ImageProcessor._cairosvg_available = True
        except (ImportError, Exception):
            ImageProcessor._cairosvg_available = False
        return ImageProcessor._cairosvg_available
    
    @staticmethod
    def convert_svg_to_png(svg_path: Path, png_path: Path, scale: int = 2) -> bool:
        """
        将SVG转换为PNG
        优先使用inkscape（效果更好），失败则尝试cairosvg
        
        Returns:
            bool: 转换是否成功
        """
        # 方法1: 尝试inkscape
        if ImageProcessor._try_inkscape(svg_path, png_path, scale):
            return True
        
        # 方法2: 尝试cairosvg
        if ImageProcessor._try_cairosvg(svg_path, png_path, scale):
            return True
            
        return False
    
    @staticmethod
    def _try_inkscape(svg_path: Path, png_path: Path, scale: int) -> bool:
        """尝试使用inkscape命令行"""
        try:
            dpi = 96 * scale
            cmd = [
                'inkscape', str(svg_path),
                '--export-type=png',
                '--export-filename', str(png_path),
                '--export-dpi', str(dpi)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and png_path.exists():
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except Exception:
            pass
        return False
    
    @staticmethod
    def _try_cairosvg(svg_path: Path, png_path: Path, scale: int) -> bool:
        """尝试使用cairosvg"""
        try:
            import cairosvg
            svg_content = svg_path.read_text(encoding='utf-8')
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=str(png_path),
                scale=scale
            )
            return png_path.exists()
        except (ImportError, Exception):
            return False
    
    @staticmethod
    def extract_svg_from_markdown(markdown: str) -> list[str]:
        """从Markdown中提取所有SVG代码"""
        import re
        pattern = r'<svg[^>]*>.*?</svg>'
        svgs = re.findall(pattern, markdown, flags=re.DOTALL | re.IGNORECASE)
        return svgs
    
    @staticmethod
    def replace_svg_with_images(
        markdown: str, 
        work_dir: Path, 
        upload_func
    ) -> str:
        """
        提取Markdown中的SVG标签，转换为PNG，上传并替换引用
        """
        svgs = ImageProcessor.extract_svg_from_markdown(markdown)
        
        if not svgs:
            return markdown
        
        work_dir.mkdir(exist_ok=True)
        
        # 首次转换前打印状态
        deps = ImageProcessor.check_dependencies()
        if not deps['inkscape'] and not deps['cairosvg']:
            print("[!] 未找到SVG转换工具 (inkscape 或 cairosvg)，内嵌SVG将保留原样")
            return markdown
        
        for i, svg_content in enumerate(svgs):
            svg_hash = hashlib.md5(svg_content.encode('utf-8')).hexdigest()[:8]
            svg_path = work_dir / f"svg_{i:03d}_{svg_hash}.svg"
            png_path = work_dir / f"svg_{i:03d}_{svg_hash}.png"
            
            svg_path.write_text(svg_content, encoding='utf-8')
            
            if ImageProcessor.convert_svg_to_png(svg_path, png_path):
                try:
                    remote_url = upload_func(str(png_path))
                    markdown = markdown.replace(svg_content, f"![image]({remote_url})")
                    print(f"[+] SVG转换成功: {svg_path.name}")
                except Exception as e:
                    print(f"[!] 上传失败 {png_path}: {e}")
            else:
                print(f"[!] SVG转换失败，保留原始代码: {svg_path.name}")
        
        return markdown


def convert_svg_to_png_simple(svg_path: str, png_path: str, scale: int = 2) -> bool:
    """
    简化接口：转换单个SVG文件为PNG
    """
    return ImageProcessor.convert_svg_to_png(Path(svg_path), Path(png_path), scale)
