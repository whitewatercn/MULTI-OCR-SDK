# 代码质量指南

## Flake8 配置说明

### 为什么忽略某些错误？

我们的 flake8 配置：
```bash
flake8 --max-line-length=88 --extend-ignore=E203,W503
```

### 被忽略的错误代码

#### ✅ E203 - whitespace before ':'

**定义**: 冒号前不应有空格

**为什么忽略**: 与 **Black** 格式化工具冲突

**示例**:
```python
# Black 会这样格式化（推荐）
my_list[start : end]  # 切片时冒号前后加空格

# Flake8 E203 会报错，认为冒号前不应有空格
# 但这是 Black 的标准格式！
```

**解决方案**: 遵循 Black 的格式，忽略 E203

**参考**:
- Black 文档: https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html
- PEP 8: 切片中的空格是可选的

---

#### ✅ W503 - line break before binary operator

**定义**: 二元运算符前不应换行

**为什么忽略**: PEP 8 **已更新**建议

**示例**:
```python
# 新风格（推荐，更易读）
total = (
    first_value
    + second_value  # 运算符在行首
    + third_value
)

# 旧风格（W503 会强制这样）
total = (
    first_value +
    second_value +  # 运算符在行尾，不易读
    third_value
)
```

**PEP 8 更新（2016）**:
> "However, for new code, the following style is suggested... break before binary operators."

**参考**:
- PEP 8 更新: https://peps.python.org/pep-0008/#should-a-line-break-before-or-after-a-binary-operator
- W503 与 W504 互相矛盾

---

#### ❌ E501 - line too long

**定义**: 行长度超过限制（默认 79，我们设置为 88）

**为什么不忽略**: 应该修复！

**我之前的错误**:
```bash
# 错误做法（不要这样）
flake8 --extend-ignore=E203,W503,E501  # ❌ 忽略行长度

# 正确做法
flake8 --max-line-length=88 --extend-ignore=E203,W503  # ✅ 只忽略冲突的规则
```

**修复方法**:
```python
# 长字符串拆分
logger.warning(
    f"Output too short ({len(text)} chars), "
    f"falling back to {self.config.fallback_mode}"
)

# 长函数调用拆分
text = await self.client.parse_async(
    file_path, mode=mode, **kwargs
)
```

---

## 为什么选择 88 字符？

**传统**: PEP 8 推荐 79 字符
**Black**: 默认使用 88 字符

**Black 的理由**:
1. 10% 更宽，能减少很多换行
2. 现代显示器足够宽
3. 依然保持可读性
4. 与 GitHub 代码审查界面兼容

**我们的选择**: 跟随 Black 的 88 字符标准

---

## 代码质量工具链

### 1. Black - 代码格式化
```bash
uv run black deepseek_ocr/
```
- **作用**: 自动格式化代码
- **风格**: 不可配置（"uncompromising"）
- **好处**: 团队统一风格，无需争论

### 2. isort - 导入排序
```bash
uv run isort deepseek_ocr/
```
- **作用**: 按字母顺序排列 import
- **配置**: `profile = "black"` 兼容 Black

### 3. Flake8 - 代码检查
```bash
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503
```
- **作用**: 检查语法错误、风格问题
- **忽略**: E203, W503（与 Black 冲突）

### 4. mypy - 类型检查
```bash
uv run mypy deepseek_ocr/
```
- **作用**: 静态类型检查
- **要求**: 100% 类型提示覆盖

### 5. pytest - 单元测试
```bash
uv run pytest tests/ -v
```
- **作用**: 运行测试套件
- **目标**: 100% 测试通过

---

## 正确的工作流

### 开发时
```bash
# 1. 写代码
vim deepseek_ocr/client.py

# 2. 格式化
uv run black deepseek_ocr/
uv run isort deepseek_ocr/

# 3. 检查
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503
uv run mypy deepseek_ocr/

# 4. 测试
uv run pytest tests/ -v
```

### 提交前
```bash
# 一键检查所有质量标准
uv run black deepseek_ocr/ && \
uv run isort deepseek_ocr/ && \
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503 && \
uv run mypy deepseek_ocr/ && \
uv run pytest tests/ -v
```

---

## pyproject.toml 配置

```toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

---

## GitHub Actions CI

我们的 `.github/workflows/test.yml`:

```yaml
- name: Run black
  run: uv run black --check deepseek_ocr/

- name: Run isort
  run: uv run isort --check-only deepseek_ocr/

- name: Run flake8
  run: |
    uv run flake8 deepseek_ocr/ \
      --max-line-length=88 \
      --extend-ignore=E203,W503

- name: Run mypy
  run: uv run mypy deepseek_ocr/
```

---

## 常见问题

### Q: 为什么不直接用 Black 的配置文件？
**A**: Black 是"零配置"工具，默认就是 88 字符。我们只需要告诉 Flake8 同样使用 88。

### Q: E203 和 W503 以后会修复吗？
**A**:
- **E203**: Flake8 维护者认为这是 Black 的问题，不会修改
- **W503**: 已经有 W504（相反的规则），建议忽略一个

### Q: 能完全关闭 Flake8 吗？
**A**: 不建议！Flake8 能捕获很多真正的错误：
- 未使用的导入
- 未定义的变量
- 语法错误
- 等等

### Q: 为什么不用 Pylint？
**A**:
- Pylint 更严格，但也更啰嗦
- Flake8 更快，规则更合理
- Black + isort + Flake8 + mypy 已经足够

---

## 总结

### ✅ 正确的忽略规则
```bash
--extend-ignore=E203,W503  # 只忽略与 Black 冲突的
```

### ❌ 错误的忽略规则
```bash
--extend-ignore=E203,W503,E501  # 不要忽略行长度！
--extend-ignore=E,W  # 不要忽略所有错误！
```

### 🎯 我们的标准
- **行长度**: 88 字符（Black 标准）
- **格式化**: Black（自动）
- **导入**: isort（自动）
- **检查**: Flake8（手动修复）
- **类型**: mypy（手动修复）
- **测试**: pytest（100% 通过）

---

## 参考资料

1. **Black**: https://black.readthedocs.io/
2. **PEP 8**: https://peps.python.org/pep-0008/
3. **Flake8**: https://flake8.pycqa.org/
4. **isort**: https://pycqa.github.io/isort/
5. **mypy**: https://mypy.readthedocs.io/

---

**最后更新**: 2025-01-05
**作者**: Chengjie
**项目**: DeepSeek-OCR-SDK
