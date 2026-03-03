# Halo Article Publisher - 故障排除指南

## 症状：发布的文章看不到图片

### 原因1：Token权限不足 ❌

**表现**：上传图片时返回 403 Forbidden

```
[!] 警告：上传图片失败 test.png: 403 Client Error: Forbidden for url: ...
```

**解决方案**：
1. 登录 Halo 管理后台
2. 进入 **访问令牌** (Access Tokens)
3. 编辑或重新生成 token，确保勾选：
   - ✅ `posts:create`
   - ✅ `posts:write`
   - ✅ **`attachments:create`** ← 这个必需！
4. 更新环境变量 `HALO_TOKEN` 为新的token
5. 重新发布

---

### 原因2：cairo未安装（SVG转换失败） ⚠️

**表现**：
```
cairosvg转换失败: no library called "cairo-2" was found
[!] SVG转换失败，保留原始代码: image.svg
```

**解决方案**：参考 `docs/CAIRO_SETUP.md` 安装cairo

**临时方案**：手动将SVG转为PNG，放到 `--images-dir` 目录

---

### 原因3：图片文件不存在或路径错误 ⚠️

**表现**：没有错误但图片未上传

**检查**：
```bash
# 确认图片文件存在
ls -la images/
# 或者相对路径
ls -la ./images/
```

**解决**：使用绝对路径或确保 `--images-dir` 正确

---

## 症状：发布失败，400错误

###  Slug重复

**错误**：`Duplicate name detected`

**已修复**：v2.0 已自动添加时间戳后缀。如仍发生，检查Halo中是否已有同名文章。

---

###  Schema验证失败

**错误**：包含"Schema Violation"或"invalid"

**常见原因**：
- categories/tags不存在于Halo
- 标题包含非法字符（Halo限制）
- 空值处理问题

**解决**：
```bash
# 使用简单分类和标签测试
python scripts/run_pipeline.py \
  --article "test.md" \
  --categories "技术" \
  --tags "测试" \
  --publish-status DRAFT  # 先存草稿
```

---

## 症状：Windows控制台乱码

**表现**：标题在终端显示为 `��������`

**原因**：Windows默认GBK编码不支持emoji

**解决**：
- ✅ **不影响实际发布**：Halo显示正常
- 如需终端正常显示，切换编码：
```cmd
chcp 65001  # UTF-8
```

---

## 症状：SVG不显示

**可能原因**：
1. cairo未安装（转换失败）
2. 转换后的PNG未上传（权限问题）
3. Halo主题不支持图片（检查主题设置）

**检查流程**：
```bash
# 1. 检查cairo
python -c "import cairosvg; print('OK')"

# 2. 查看发布日志
# 应看到: [+] SVG转换成功: xxx.png

# 3. 登录Halo后台查看文章
# - 检查内容区域是否有 <img> 标签
# - 直接访问图片URL（右键复制图片地址）
```

---

## 快速诊断脚本

运行 `scripts/check_cairo.bat` 检查环境：

```batch
=== Cairo Environment Checker

[+] cairosvg module found
[*] Checking cairo library...
[+] cairo works!
```

或者使用测试脚本：
```bash
python test_skill.py
```

---

## 完整发布命令示例

### 正常发布（带图片）
```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --images-dir "./images" \
  --cover "cover.jpg" \
  --categories "技术,Python" \
  --tags "教程,AI" \
  --publish-status PUBLISHED
```

### 先存草稿测试
```bash
python scripts/run_pipeline.py \
  --article "article.md" \
  --publish-status DRAFT
```

然后在Halo后台预览，确认无误后再发布。

---

## 权限设置截图（Halo后台）

1. 头像 → **Access Tokens**
2. 点击token名称编辑
3. 角色选择：**admin**（或自定义角色）
4. 权限勾选：
   ```
   Content > Posts
     - posts:create
     - posts:write
   Content > Attachments
     - attachments:create  ← 必须有！
   ```
5. 保存

---

## 如果还是不行

1. **查看详细日志**：
   ```bash
   python scripts/run_pipeline.py ... 2>&1 | tee publish.log
   ```

2. **检查Halo后台**：
   - 文章是否创建成功（列表页）
   - 附件是否上传（媒体库）
   - API日志（如果有）

3. **简化测试**：
   ```bash
   # 最小化测试
   echo "# Test" > test.md
   python scripts/run_pipeline.py --article test.md --publish-status DRAFT
   ```

4. **提交Issue**：
   - 包含 `publish.log`
   - Halo版本号
   - 操作系统
   - 重现步骤

---

## 已发布文章看不到图片怎么办？

1. **检查图片上传是否成功**：
   - 日志中应有 `[+] 处理图片目录` 和上传成功消息
   - 如果没有，说明图片未被处理

2. **登录Halo后台查看**：
   - 文章编辑页面，查看图片链接是否指向你的域名
   - 媒体库中是否有上传的图片

3. **如果图片链接是相对路径或本地路径**：
   - 说明上传失败，检查token权限（403错误）
   - 或检查网络连接

4. **如果图片链接是完整URL但前端不显示**：
   - 浏览器访问该URL，查看是否能打开
   - 检查Halo主题设置（可能禁用了图片懒加载）

---

## 重新发布已存在的文章

如果需要重新发布（修复错误）：

```bash
# 使用不同的slug（新标题或添加后缀）
# or manually delete the old post in Halo admin first
```

Halo不允许slug重复，v2.0已自动添加时间戳避免冲突。

---

**最后更新**: 2025-02-28  
**适用版本**: v2.0+
