# 🚀 Halo Article Publisher - 快速上手指南

## ✅ 当前状态

你的 skill 已安装并升级到 **v2.0**：
- ✅ 基础发布功能正常
- ✅ SVG转换代码就绪
- ⚠️ 需要 cairo 库支持SVG转换
- ⚠️ 需要 Halo token 有 `attachments:create` 权限才能上传图片

---

## 🎯 三步使用这个Skill

### 第1步：检查Halo Token权限 ⚠️ 重要！

**必须**有 `attachments:create` 权限，否则图片无法上传。

1. 登录 Halo 管理后台
2. 头像 → Access Tokens
3. 编辑你的token
4. 确保勾选：
   - ✅ `posts:create`
   - ✅ `posts:write`
   - ✅ **`attachments:create`**
5. 重新生成token或保存
6. 更新环境变量：
   ```bash
   export HALO_TOKEN="new-token-here"
   ```

---

### 第2步：安装cairo（可选但推荐）

如果文章包含SVG图表/图形，需要cairo支持。

**最简单**：安装 MSYS2 然后 `pacman -S mingw-w64-ucrt-x86_64-cairo`

详细步骤：见 `docs/CAIRO_SETUP.md`

**跳过cairo**：文章中的SVG会保留原始代码，Halo可能不显示。可手动转PNG后用 `--images-dir` 发布。

---

### 第3步：发布文章

#### 简单文章（无图片）
```bash
python scripts/run_pipeline.py \
  --article "文章.md" \
  --publish-status PUBLISHED
```

#### 带图片的文章
```bash
# 确保图片在 ./images 目录
python scripts/run_pipeline.py \
  --article "文章.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --publish-status PUBLISHED
```

#### 测试用（先存草稿）
```bash
python scripts/run_pipeline.py \
  --article "文章.md" \
  --publish-status DRAFT
```
在Halo后台预览无误后再发布。

---

## 📝 示例工作流

### 1. 准备文件和图片
```
my-article/
├── article.md          # 你的文章（支持Markdown + 内嵌SVG）
├── images/            # 图片目录
│   ├── diagram.svg    # SVG会被自动转换
│   ├── photo.jpg
│   └── cover.png
```

### 2. 测试依赖
```bash
cd halo-auto-article-publisher
python test_skill.py
# 期望: 3/3 tests passed
```

### 3. 检查cairo（如果需要SVG）
```bash
scripts/check_cairo.bat
# 期望: [+] cairo works!
```

### 4. 发布
```bash
python scripts/run_pipeline.py \
  --article "../my-article/article.md" \
  --images-dir "../my-article/images" \
  --cover "../my-article/images/cover.png" \
  --categories "AI,Agent" \
  --tags "上下文工程,LLM" \
  --publish-status PUBLISHED
```

---

## 🧪 验证发布结果

1. **访问你的Halo站点**
   - 查看文章是否能打开
   - 图片是否显示

2. **如图片不显示，检查**：
   - 是否看到警告：`403 Forbidden` → 检查token权限
   - 是否看到警告：`SVG转换失败` → 安装cairo
   - 在Halo后台编辑文章，查看图片URL是否正确

3. **查看上传的图片**：
   - Halo后台 → 媒体库
   - 应该有上传的图片文件

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| `SKILL.md` | Skill定义和完整使用说明 |
| `README.md` | 详细文档（原版） |
| `INSTALL.md` | 安装配置指南 |
| `TROUBLESHOOTING.md` | 故障排除 |
| `docs/CAIRO_SETUP.md` | cairo库安装（SVG支持） |
| `CHANGELOG_v2.md` | 版本更新日志 |
| `MODIFICATION_REPORT.md` | v2.0修改报告 |

---

## ⚡ 一键测试

```bash
# 1. 检查模块
python test_skill.py

# 2. 检查cairo（如需SVG）
scripts/check_cairo.bat

# 3. 发布测试文章（最简单的）
echo "# Hello Halo" > test.md
python scripts/run_pipeline.py --article test.md --publish-status DRAFT
```

---

## 🆘 常见问题快速答案

| 问题 | 答案 |
|------|------|
| 图片上传失败403 | Token缺 `attachments:create` 权限 |
| SVG不显示 | 安装cairo（MSYS2）或手动转PNG |
| 发布成功但无内容 | 检查文章路径是否正确`--article` |
| 中文标题乱码 | 正常，Halo显示正常，终端乱码可忽略 |
| 想先预览再发布 | 用 `--publish-status DRAFT` |
| 需要支持哪些图片格式 | jpg, png, gif, webp，svg会自动转PNG |

---

## 🔧 高级用法

### 批量发布
```bash
for f in articles/*.md; do
  python scripts/run_pipeline.py --article "$f" --publish-status DRAFT
done
```

### 覆盖环境变量
```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --halo-base-url "https://staging.halo.com" \
  --halo-token "temp-token"
```

### 指定模板
```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --template "my-custom-template" \
  --publish-status PUBLISHED
```

---

## 🎉 你已准备好

Happy Publishing! 🚀

如有问题，查看 `TROUBLESHOOTING.md` 或提交 Issue。
