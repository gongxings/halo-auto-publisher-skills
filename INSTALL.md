# Halo Article Publisher - 安装与配置指南

## ✅ Skill 已就绪

你的 `halo-article-publisher` skill 已安装在：
```
.opencode/skills/halo-auto-article-publisher/
```

已包含的功能：
- ✅ SVG自动转换（需Inkscape/cairo）
- ✅ 内容优化与Windows兼容
- ✅ 智能slug生成
- ✅ 详细日志输出
- ✅ 完整错误处理

## 🔧 环境配置

### 1. Halo 环境变量

在你的shell或.bashrc/.zshrc中设置：

```bash
export HALO_BASE_URL="https://your-halo-site.com"
export HALO_TOKEN="your-access-token-here"
```

或者在每次发布时通过参数覆盖：
```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --halo-base-url "https://your-site.com" \
  --halo-token "your-token"
```

### 2. 可选：SVG 转换依赖

如果要支持内嵌SVG转换（推荐）：

#### 方案A：安装 Inkscape（推荐🚀）

Inkscape提供最佳的SVG渲染质量，支持所有SVG特性。

1. 下载：https://inkscape.org/release/inkscape-1.4/
2. 安装到默认路径
3. 测试：
```bash
inkscape --version
# 应输出: Inkscape 1.4 (或更高)
```

#### 方案B：安装 cairosvg + cairo

cairosvg是纯Python库，但需要系统cairo库。

**Windows：**
```bash
# 安装GTK3 runtime (包含cairo)
# 下载: https://www.gtk.org/docs/installations/windows/
# 或使用MSYS2: pacman -S mingw-w64-x86_64-cairo

# 然后安装cairosvg
pip install cairosvg
```

**macOS:**
```bash
brew install cairo
pip install cairosvg
```

**Linux (Ubuntu/Debian):**
```bash
apt-get install libcairo2
pip install cairosvg
```

**测试cairosvg:**
```bash
python -c "import cairosvg; print('OK')"
```

## 🚀 使用方法

### 基本用法

```bash
cd halo-auto-article-publisher
python scripts/run_pipeline.py \
  --article "path/to/article.md" \
  --publish-status PUBLISHED
```

### 带图片目录

```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --publish-status PUBLISHED
```

### 带封面和分类

```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --categories "技术,Python,教程" \
  --tags "AI,Agent,LLM" \
  --publish-status PUBLISHED
```

### 保存为草稿

```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --publish-status DRAFT
```

## 🧪 测试Skill功能

运行内置测试：

```bash
cd halo-auto-article-publisher
python test_skill.py
```

应该看到：
```
[*] Testing Halo Article Publisher Skill

--- Module Imports ---
[+] ImageProcessor imported successfully
[+] Dependencies: Inkscape=True/False, Cairosvg=True/False
[+] Module Imports: PASS

--- Slug Generation ---
[+] Slug test: 'Hello World' -> 'hello-world'
[+] Slug Generation: PASS

--- SVG Extraction ---
[+] Found 1 SVG(s) in test markdown
[+] SVG Extraction: PASS

==================================================
Summary: 3/3 tests passed
[+] All tests passed! Skill is ready to use.
```

## 📊 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 基础发布 | ✅ | 支持Halo 2.x Console API |
| 图片上传 | ✅ | 自动替换本地引用为远程URL |
| SVG转换 | ✅ | 内嵌<svg>和.svg文件自动转PNG |
| 封面SVG | ✅ | 封面支持SVG格式 |
| 内容优化 | ✅ | Windows编码、空行规范化 |
| Slug唯一性 | ✅ | 自动加时间戳避免冲突 |
| 分类标签 | ✅ | 支持categories和tags |
| 草稿模式 | ✅ | --publish-status DRAFT |
| 日志输出 | ✅ | 详细的状态信息 |
| 错误恢复 | ✅ | 单个图片失败不影响整体 |

## ⚠️ 已知限制

1. **SVG转换需要外部工具**
   - 如果没有Inkscape或cairo，SVG会保留原始代码，可能导致显示问题
   - 解决：安装Inkscape或手动转换SVG为PNG

2. **Windows控制台编码**
   - Windows默认GBK编码可能导致emoji显示乱码
   - 不影响实际发布内容，Halo显示正常

3. **Slug长度限制**
   - Halo slug限制100字符
   - 超长标题会自动截断

4. **网络超时**
   - 上传大文件可能需要60秒以上
   - 可修改`halo_client.py`中的timeout值

## 🐛 故障排除

### SVG未转换
```bash
# 检查工具可用性
inkscape --version
python -c "import cairosvg; print('cairosvg OK')"

# 如果都不可用，SVG会保留原始代码
# 建议安装Inkscape: https://inkscape.org/
```

### 400错误 - Duplicate name
已自动处理（slug加时间戳）。如仍发生，检查Halo中是否有同名文章。

### 400错误 - Schema violation
确保categories/tags存在或为有效字符串。空值会发送空数组。

### 图片上传失败
- 检查文件权限
- 确保文件存在且可读
- Halo存储空间是否充足

## 📝 版本历史

### v2.0 (2025-02-28)
- ✨ 新增SVG自动转换（Inkscape/cairosvg）
- ✨ 新增内容优化（Windows兼容）
- ✨ 改进slug生成（总是唯一）
- 🐛 修复slug重复bug
- 🐛 改进错误处理和日志

### v1.0 (Original)
- 基础发布功能
- 图片上传
- 分类标签支持

## 🔗 相关资源

- **Halo 官网**: https://halo.run/
- **Halo 文档**: https://docs.halo.run/
- **Inkscape**: https://inkscape.org/
- **cairosvg**: https://cairosvg.io/

## 📧 支持

遇到问题？
1. 查看本指南的"故障排除"部分
2. 运行`python test_skill.py`检查依赖
3. 提交Issue: https://github.com/your-repo/issues

---

**Happy Publishing! 🚀**

Last updated: 2025-02-28
