# Cairo 安装指南（Windows）

由于cairosvg依赖cairo图形库，在Windows上需要额外安装。有两种方案：

---

## 方案A：使用 MSYS2（推荐，约500MB）

MSYS2提供完整的UNIX-like环境，包含cairo库。

### 步骤1：下载安装MSYS2

访问 https://www.msys2.org/  
下载 `msys2-x86_64-20240903.exe`（或最新版）  
运行安装程序，按默认设置安装到 `C:\msys64`

### 步骤2：更新系统

打开 **MSYS2 MSYS**（开始菜单 → MSYS2 → MSYS2）  
依次运行：

```bash
# 更新包数据库
pacman -Syu

# 重启MSYS2（如果提示）
# 然后再次运行更新直到成功
pacman -Syu
```

### 步骤3：安装cairo

```bash
# 安装cairo（包含cairo、glib等依赖）
pacman -S mingw-w64-ucrt-x86_64-cairo
```

### 步骤4：添加环境变量

将以下路径添加到系统PATH（重启终端）：

```
C:\msys64\ucrt64\bin
```

### 步骤5：验证

```bash
python -c "import cairosvg; print('OK')"
```
如果输出`OK`，表示安装成功。

---

## 方案B：使用预编译的GTK3 bundle（约150MB）

从gvsbuild项目下载预编译的GTK3，包含cairo。

### 步骤1：下载

访问 https://github.com/wingtk/gvsbuild/releases  
下载最新版 `gtk3-vs2022-x64-YYYY-MM-DD.zip`

### 步骤2：解压

解压到任意目录，例如 `D:\gtk3-runtime`

### 步骤3：设置环境变量

**临时**（每次打开终端前运行）：
```bash
set CAIRO_LIBRARY_PATH=D:\gtk3-runtime\bin
set PATH=D:\gtk3-runtime\bin;%PATH%
```

**永久**（系统属性 → 环境变量）：
- 添加 `CAIRO_LIBRARY_PATH` = `D:\gtk3-runtime\bin`
- 编辑 `PATH`，添加 `D:\gtk3-runtime\bin`

### 步骤4：验证

```bash
python -c "import cairosvg; print('OK')"
```

---

## 方案C：使用conda（如果已安装）

```bash
conda install -c conda-forge cairo
```

---

## 测试 cairosvg

安装后运行：

```bash
cd halo-auto-article-publisher
python test_skill.py
```

应该看到：
```
[+] Dependencies: Inkscape=False, Cairosvg=True
```

---

## 故障排除

### "ImportError: no module named 'cairo'"
- cairo未安装或不在PATH中
- 确认 `CAIRO_LIBRARY_PATH` 指向包含 `cairo.dll` 的目录

### "cannot find library 'libcairo-2.dll'"
- 缺少cairo DLL
- 使用`where cairo.dll`检查DLL是否在PATH中

### cairosvg导入成功但转换失败
- 检查cairo版本兼容性
- 尝试重新安装：

```bash
pip uninstall -y cairosvg cairocffi
pip install cairosvg
```

---

## 我需要cairo吗？

**是**，如果要支持内嵌SVG转换。否则：
- 内嵌SVG会保留原始代码
- Halo可能不渲染这些SVG标签
- 文章显示会看到SVG源码

**建议**：安装cairo，享受完整的自动SVG转换功能。

---

## 快速验证脚本

运行 `check_cairo.bat`（Windows）或 `check_cairo.sh`（Linux/macOS）：

```batch
@echo off
python -c "import cairosvg; import io; output = io.BytesIO(); cairosvg.svg2png(bytestring=b'<svg width=\"1\" height=\"1\"></svg>', write_to=output); print('Cairo + cairosvg OK')" 2>&1
pause
```

如果看到绿色字 OK，就配置好了。
