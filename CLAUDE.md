# Claude Code 开发指南

本文档记录使用 Claude Code 开发本项目时的重要规范和经验教训。

## 基本规范

- 流程图使用Mermaid格式

## Python 类型检查最佳实践

### 背景

在 2025-01-05 的开发中，遇到了 21 个 mypy 类型检查错误，主要集中在：
- `Optional[int]` 和 `Optional[str]` 类型处理
- `Dict[str, Any]` 返回类型推断
- 第三方库类型存根缺失

### 常见类型错误及解决方案

#### 1. Optional 参数的默认值

**❌ 错误写法：**
```python
def __init__(self, message: str, status_code: int = None):
    pass
```

**错误信息：**
```
error: Incompatible default for argument "status_code" (default has type "None", argument has type "int")
note: PEP 484 prohibits implicit Optional
```

**✅ 正确写法：**
```python
from typing import Optional

def __init__(self, message: str, status_code: Optional[int] = None):
    pass
```

**原因：** PEP 484 禁止隐式 Optional。如果参数默认值是 `None`，必须显式标注 `Optional[类型]`。

---

#### 2. 环境变量和字典 get() 方法的类型处理

**❌ 错误写法：**
```python
api_key: str = overrides.get("api_key") or os.getenv("DS_OCR_API_KEY", "")
# 错误：expression has type "Optional[str]", variable has type "str"
```

**问题：**
- `dict.get()` 返回 `Optional[V]`
- `os.getenv()` 返回 `Optional[str]`
- mypy 不理解 `or` 运算符保证非 None

**✅ 解决方案 1：使用 cast()**
```python
from typing import cast

api_key = cast(str, overrides.get("api_key") or os.getenv("DS_OCR_API_KEY", ""))
```

**✅ 解决方案 2：显式处理 None**
```python
api_key_raw = overrides.get("api_key") or os.getenv("DS_OCR_API_KEY")
api_key = api_key_raw if api_key_raw else ""
```

**推荐：** 在确定逻辑保证非 None 时使用 `cast()`，更简洁。

---

#### 3. JSON 响应的 Any 类型

**❌ 错误写法：**
```python
def _make_api_request(self) -> Dict[str, Any]:
    result = await response.json()  # mypy 推断为 Any
    return result  # error: Returning Any from function
```

**✅ 正确写法：**
```python
def _make_api_request(self) -> Dict[str, Any]:
    result: Dict[str, Any] = await response.json()
    return result
```

**原因：** 给中间变量添加显式类型注解，避免 mypy 推断为 `Any`。

---

#### 4. 第三方库类型存根缺失

**❌ 错误信息：**
```
error: Library stubs not installed for "requests"
note: Hint: "python3 -m pip install types-requests"
```

**✅ 解决方案：**

在 `pyproject.toml` 中添加类型存根包：
```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.4.0",
    "types-requests>=2.28.0",  # 添加这行
]
```

然后运行：
```bash
uv sync --all-extras
```

---

#### 5. 可变参数的类型注解

**❌ 错误写法：**
```python
def __init__(self, **kwargs: Optional[str]):
    pass
```

**错误：** `**kwargs` 不能是 Optional，因为字典值本身可以是任意类型。

**✅ 正确写法：**
```python
# 如果所有值都是字符串
def __init__(self, **kwargs: str):
    pass

# 如果值可能是不同类型
def __init__(self, **kwargs: Any):
    pass
```

---

### mypy 配置建议

在 `pyproject.toml` 中：

```toml
[tool.mypy]
python_version = "3.9"  # 使用 3.9+，不要用 3.8（不支持某些特性）
warn_return_any = true  # 警告返回 Any
warn_unused_configs = true  # 警告未使用的配置
disallow_untyped_defs = false  # 根据项目需求决定
ignore_missing_imports = true  # 忽略第三方库缺失的类型存根
```

---

### 完整的 CI 检查流程

开发时按顺序执行：

```bash
# 1. 自动格式化
uv run black deepseek_ocr/
uv run isort deepseek_ocr/

# 2. 代码检查
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503
uv run mypy deepseek_ocr/

# 3. 测试
uv run pytest tests/ -v

# 4. 一键检查所有（提交前）
uv run black --check deepseek_ocr/ && \
uv run isort --check-only deepseek_ocr/ && \
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503 && \
uv run mypy deepseek_ocr/ && \
uv run pytest tests/ -v
```

---

### 类型检查错误优先级

遇到 mypy 错误时，按优先级处理：

1. **高优先级（必须修复）：**
   - `incompatible type in assignment`
   - `incompatible return value`
   - `no attribute`

2. **中优先级（应该修复）：**
   - `implicit Optional`
   - `returning Any`
   - `missing type annotation`

3. **低优先级（可以忽略）：**
   - 第三方库类型存根缺失（如果已安装 `types-*` 包仍报错）

---

### 经验教训总结

1. **永远不要忽略真正的类型错误**
   - ❌ 不要用 `# type: ignore` 掩盖问题
   - ✅ 找到根本原因并修复

2. **使用 cast() 需谨慎**
   - ✅ 仅在确定逻辑保证类型安全时使用
   - ❌ 不要用 cast() 强制转换不兼容的类型

3. **保持类型注解的一致性**
   - 函数签名、返回值、变量赋值都要有清晰的类型注解
   - 避免让 mypy 推断为 `Any`

4. **及时安装类型存根包**
   - 使用第三方库时，检查是否有对应的 `types-*` 包
   - 在 `pyproject.toml` 的 `dev` 依赖中统一管理

5. **CI 失败时立即修复**
   - 不要积累类型错误
   - 每次提交前确保本地 CI 检查全部通过

---

### 相关文档

- [CODE_QUALITY_GUIDE.md](./CODE_QUALITY_GUIDE.md) - Flake8 规则说明
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [mypy 官方文档](https://mypy.readthedocs.io/)

---

**最后更新：** 2025-01-05
**错误修复记录：** 从 21 个 mypy 错误降至 0 个