# Halo Article Publisher - 更新日志

## v2.0 - SVG支持与内容优化 (2025-02-28)

### 🎉 新功能

1. **SVG自动转换**
   - 自动检测并转换内嵌的 `<svg>` 标签为PNG
   - 支持图片引用中的 `.svg` 文件
   - 支持封面图片为SVG格式
   - 双转换引擎：优先Inkscape，fallback到Cairosvg

2. **内容优化**
   - 优化Windows编码兼容性
   - 清理可能引起问题的HTML标签
   - 规范化空行和格式

3. **图片处理增强**
   - 统一的图片处理器 `ImageProcessor`
   - 自动创建临时工作目录
   - 更详细的处理日志

### 📦 新增文件

- `scripts/image_processor.py` - 图片处理模块
  - `convert_svg_to_png()` - SVG转PNG（支持inkscape/cairosvg）
  - `extract_svg_from_markdown()` - 提取SVG代码
  - `replace_svg_with_images()` - 批量处理并替换

### 🔧 使用方法

#### 基本用法（自动处理SVG）

```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --publish-status PUBLISHED
```

如果文章包含内嵌SVG，会自动：
1. 提取SVG
2. 转换为PNG
3. 上传到Halo
4. 替换为图片链接

#### 配合图片目录

```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.svg" \  # 支持SVG封面
  --publish-status PUBLISHED
```

#### 总结

| 类型 | 之前 | 现在 |
|------|------|------|
| 内嵌`<svg>` | 显示乱码 | ✅ 自动转PNG上传 |
| 图片目录中的.svg | 无法上传 | ✅ 自动转换 |
| SVG封面 | 可能失败 | ✅ 完美支持 |
| 依赖 | 无 | 可选inkscape/cairosvg |

### ⚠️ 注意事项

1. **依赖安装**（可选）：
   ```bash
   # 安装cairosvg（纯Python）
   pip install cairosvg
   
   # 或者安装Inkscape（效果更好）
   # Windows: https://inkscape.org/release/inkscape-1.4/
   # Mac: brew install --cask inkscape
   # Linux: apt-get install inkscape
   ```

2. **转换质量**：
   - Inkscape效果最佳（推荐）
   - Cairosvg作为fallback
   - 如果都没有，会跳过SVG并给出警告

3. **性能**：
   - SVG转换需要额外时间（每张约1-3秒）
   - 建议提前准备PNG版本以加速发布

4. **调试**：
   - 查看控制台输出，确认"✓ SVG转换并上传成功"
   - 如有失败，会显示警告信息

### 🐛 修复

- 修复了封面图片为SVG时可能失败的问题
- 改进错误处理，单个图片失败不影响整体发布
- 优化日志输出，更清晰的处理状态

### 📝 迁移指南

如果你已有老版本：

1. 无需修改使用方式
2. 新增的SVG处理完全自动
3. 建议测试一篇含SVG的文章验证功能

```bash
# 原命令仍然有效
python scripts/run_pipeline.py --article "test.md" --images-dir "./images"
```

---

**Happy Publishing! 🚀**
