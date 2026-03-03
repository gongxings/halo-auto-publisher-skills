#!/usr/bin/env python3
"""
自动安装cairo运行时依赖（Windows）
This script downloads and configures GTK3 runtime for cairosvg on Windows.
"""

import os
import sys
import zipfile
import tempfile
from pathlib import Path
import urllib.request

def download_gtk3_runtime():
    """下载GTK3 runtime bundle"""
    # GTK3 Runtime for Windows (from gvsbuild)
    # https://github.com/wingtk/gvsbuild/releases
    
    # 使用预编译的GTK3 bundle
    url = "https://github.com/wingtk/gvsbuild/releases/download/2024-02-04/gtk3-vs2022-x64-2024-02-04.zip"
    
    print(f"[+] Downloading GTK3 runtime from {url}...")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            return tmp.name
    except Exception as e:
        print(f"[!] Download failed: {e}")
        return None

def setup_cairo():
    """设置cairo环境"""
    print("[*] Setting up cairo for cairosvg...")
    
    # 检查是否已安装
    try:
        import cairosvg
        import io
        output = io.BytesIO()
        cairosvg.svg2png(bytestring=b'<svg width="1" height="1"></svg>', write_to=output)
        print("[+] cairosvg already works!")
        return True
    except Exception:
        pass
    
    # 尝试使用conda（如果可用）
    try:
        import subprocess
        result = subprocess.run(['conda', '--version'], capture_output=True)
        if result.returncode == 0:
            print("[+] Conda detected. You can install cairo with:")
            print("    conda install -c conda-forge cairo")
            return True
    except:
        pass
    
    # 嵌入式GTK3方案
    print("[*] Downloading GTK3 runtime (embedded approach)...")
    zip_path = download_gtk3_runtime()
    if not zip_path:
        return False
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 解压到项目目录下的gtk3-runtime
            target_dir = Path(__file__).parent / "gtk3-runtime"
            target_dir.mkdir(exist_ok=True)
            zip_ref.extractall(target_dir)
            print(f"[+] Extracted to {target_dir}")
    except Exception as e:
        print(f"[!] Extraction failed: {e}")
        return False
    finally:
        try:
            os.unlink(zip_path)
        except:
            pass
    
    # 设置环境变量
    bin_path = target_dir / "bin"
    if bin_path.exists():
        print(f"[+] Adding {bin_path} to CAIRO_LIBRARY_PATH")
        os.environ['CAIRO_LIBRARY_PATH'] = str(bin_path)
        # 同时添加到PATH（临时）
        os.environ['PATH'] = f"{bin_path};{os.environ.get('PATH', '')}"
        
        # 测试
        try:
            import cairosvg
            import io
            output = io.BytesIO()
            cairosvg.svg2png(bytestring=b'<svg width="1" height="1"></svg>', write_to=output)
            print("[+] cairosvg works now!")
            return True
        except Exception as e:
            print(f"[!] Still not working: {e}")
            return False
    else:
        print(f"[!] bin directory not found in {target_dir}")
        return False

def main():
    print("=== Cairo Dependency Installer ===\n")
    
    # 获取skill目录
    skill_dir = Path(__file__).parent
    print(f"[*] Skill directory: {skill_dir}")
    
    if setup_cairo():
        print("\n[+] Setup successful!")
        print("\nTo use permanently, add these to your environment or run this script before publishing:")
        print(f'set CAIRO_LIBRARY_PATH={skill_dir / "gtk3-runtime" / "bin"}')
        print("or on PowerShell:")
        print(f'$env:CAIRO_LIBRARY_PATH="{skill_dir / "gtk3-runtime" / "bin"}"')
        return 0
    else:
        print("\n[!] Setup failed.")
        print("\nAlternative: Install Inkscape from https://inkscape.org/")
        print("Inkscape provides better SVG rendering and is easier to install.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
