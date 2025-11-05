# 测试清单 - PyPI 发布前必须完成

## ⚠️ 重要提示

**在发布到 PyPI 之前，必须完成以下所有测试！**

---

## 1. 单元测试 ✅

### 已完成
- [x] 配置管理测试 (5个测试)
- [x] 枚举类型测试 (3个测试)
- [x] 异常测试 (5个测试)

### 待完成
- [ ] OCR 客户端测试（使用 mock）
  - [ ] `parse()` 方法
  - [ ] `parse_async()` 方法
  - [ ] PDF 转 Base64
  - [ ] 错误处理
  - [ ] 智能回退机制
- [ ] 批量处理测试（使用 mock）
  - [ ] 单文档处理
  - [ ] 批量处理
  - [ ] 错误重试
  - [ ] 进度跟踪

---

## 2. 集成测试 ❌

**需要真实的 API Key 和测试文档**

### 必须测试的场景

#### 2.1 基础 OCR 功能
- [ ] FREE_OCR 模式处理简单 PDF
- [ ] GROUNDING 模式处理复杂表格
- [ ] OCR_IMAGE 模式测试
- [ ] 中文文档处理（chinese_hint=True）
- [ ] 不同 DPI 设置（150, 200, 300）

#### 2.2 错误处理
- [ ] API 密钥错误
- [ ] 文件不存在
- [ ] 无效文件格式
- [ ] 网络超时
- [ ] API 限流（429 错误）
- [ ] API 服务器错误（500 错误）

#### 2.3 智能回退
- [ ] 输出 < 500 字符时自动切换到 GROUNDING
- [ ] 回退机制配置（fallback_enabled）

#### 2.4 批量处理
- [ ] 并发处理 3-5 个文档
- [ ] 错误重试机制
- [ ] 进度显示

---

## 3. 性能测试 ❌

### 测试指标
- [ ] 单文档处理时间（FREE_OCR vs GROUNDING）
- [ ] 批量处理吞吐量
- [ ] 内存使用情况
- [ ] 并发性能（不同 max_concurrent 值）

### 对比基准
- [ ] 与文档中声称的性能数据对比
  - FREE_OCR: 3.95-10.95秒
  - GROUNDING: 5.18-8.31秒

---

## 4. 兼容性测试 ❌

### Python 版本
- [ ] Python 3.8.1
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12

### 操作系统
- [ ] Linux (Ubuntu)
- [ ] macOS
- [ ] Windows

### 依赖兼容性
- [ ] uv 安装
- [ ] pip 安装
- [ ] 所有依赖正确安装

---

## 5. 文档验证 ❌

### 示例代码
- [ ] `examples/01_basic_usage.py` 可运行
- [ ] `examples/02_batch_processing.py` 可运行
- [ ] README 中的示例代码可运行
- [ ] API_REFERENCE 中的示例代码可运行

### 文档准确性
- [ ] API 参数说明正确
- [ ] 性能数据真实可信
- [ ] 错误信息描述准确

---

## 6. 端到端测试 ❌

### 完整工作流
- [ ] 安装包 → 配置 → 运行示例
- [ ] 不同场景的真实使用案例
  - [ ] 发票识别
  - [ ] 复杂表格提取
  - [ ] 中文证书识别
  - [ ] 批量文档处理

---

## 7. 打包测试 ❌

### 本地测试
- [ ] `uv build` 成功
- [ ] 生成的 wheel 文件正确
- [ ] 安装到虚拟环境测试
- [ ] 从 wheel 安装后功能正常

### TestPyPI 测试
- [ ] 发布到 TestPyPI
- [ ] 从 TestPyPI 安装
- [ ] 安装后功能测试

---

## 测试脚本

### 快速测试脚本（需要 API Key）

```bash
# 设置 API Key
export DS_OCR_API_KEY="your_real_api_key"

# 准备测试文档
mkdir -p test_docs
# 放入一些测试 PDF 文件

# 测试基础功能
cd /Users/chengjie/projects/Deepseek-OCR-SDK
uv run python << 'EOF'
from deepseek_ocr import DeepSeekOCR
import os

# 测试基础 OCR
client = DeepSeekOCR(api_key=os.getenv("DS_OCR_API_KEY"))
text = client.parse("test_docs/simple.pdf")
print(f"✓ 基础 OCR 测试通过: {len(text)} 字符")

# 测试 GROUNDING 模式
text = client.parse("test_docs/table.pdf", mode="grounding")
print(f"✓ GROUNDING 模式测试通过: {len(text)} 字符")

# 测试中文
text = client.parse("test_docs/chinese.pdf", chinese_hint=True)
print(f"✓ 中文文档测试通过: {len(text)} 字符")

print("\n✅ 所有基础测试通过！")
EOF

# 测试批量处理
uv run python examples/02_batch_processing.py

# 运行单元测试
uv run pytest tests/ -v

# 代码质量检查
uv run black --check deepseek_ocr/
uv run mypy deepseek_ocr/
uv run flake8 deepseek_ocr/
```

---

## 建议的发布流程

### Phase 1: 本地完整测试 ⏳
1. 完成所有单元测试
2. 使用真实 API 进行集成测试
3. 运行示例代码验证
4. 修复发现的所有 bug

### Phase 2: TestPyPI 测试 ⏳
```bash
# 构建包
uv build

# 发布到 TestPyPI
uv run twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ deepseek-ocr

# 验证安装和功能
python -c "from deepseek_ocr import DeepSeekOCR; print('导入成功')"
```

### Phase 3: 正式发布 ⏳
只有在 Phase 1 和 2 完全通过后才进行：
```bash
# 打标签
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 创建 GitHub Release（自动触发 PyPI 发布）
```

---

## 当前状态总结

✅ **已完成**：
- 代码结构完整
- 基础单元测试通过
- 文档完整
- GitHub 发布成功

❌ **待完成（发布前必须）**：
- 使用真实 API 的集成测试
- 完整的错误场景测试
- 性能基准验证
- 跨平台兼容性测试
- TestPyPI 试发布

⚠️ **建议**：
**不要急于发布到 PyPI！先完成测试，确保质量。**

---

## 下一步行动

1. **获取测试资源**
   - [ ] 准备 5-10 个测试文档（简单文档、复杂表格、中文文档）
   - [ ] 确认 API Key 可用
   - [ ] 准备测试环境

2. **执行测试**
   - [ ] 按照上述清单逐项测试
   - [ ] 记录测试结果
   - [ ] 修复发现的问题

3. **文档更新**
   - [ ] 更新性能数据（使用真实测试结果）
   - [ ] 补充已知问题和限制
   - [ ] 完善故障排除指南

4. **发布准备**
   - [ ] 完成所有测试
   - [ ] 更新 CHANGELOG
   - [ ] 准备 Release Notes

---

**记住：质量第一，不要急于发布！**

测试完成后，我们可以信心满满地发布到 PyPI。
