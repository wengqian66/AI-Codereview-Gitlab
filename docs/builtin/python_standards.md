# Python编码规范

**Python代码规范 | Python编程标准 | Python最佳实践 | Python代码审查**

Python编程语言的编码规范和最佳实践指南，适用于代码审查和质量控制。

---

## 一、代码质量规范

### 1.1 可读性与维护性

#### 遵循PEP 8规范
- 4个空格缩进，不使用Tab
- 每行最大79字符（文档字符串72字符）
- 空行分隔函数和类
- 导入顺序：标准库、第三方库、本地库

#### 禁止重复代码
- 同一段代码在多个地方重复出现时，必须提取为公共函数或工具类
- 遵循DRY（Don't Repeat Yourself）原则

#### 方法复杂度限制
- 单个函数的圈复杂度（分支数）不得超过10，否则需拆分子函数
- 使用工具检测圈复杂度，如pylint、flake8

#### 清除无效代码
- 注释掉的代码必须删除
- 未使用的导入和变量必须删除

### 1.2 面向对象设计

#### 类设计原则
- 遵循单一职责原则，每个类只负责一个功能领域
- 使用私有属性和方法（以_开头）进行封装

#### 继承与组合
- 优先使用组合而非继承
- 继承时使用super()调用父类方法

#### 特殊方法
- 正确实现__init__、__str__、__repr__等特殊方法
- 使用@property装饰器定义属性

## 二、安全规范

### 2.1 输入与输出安全

#### SQL注入防护
- 禁止拼接SQL语句
- 必须使用参数化查询或ORM框架

**示例**：
```python
# 正确：使用参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# 错误：直接拼接
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

#### 路径遍历防护
- 用户提供的文件路径必须校验合法性
- 使用os.path.normpath()规范化路径

#### 命令注入防护
- 禁止使用os.system()、subprocess.call()执行用户输入
- 使用subprocess.run()并设置shell=False

### 2.2 敏感信息保护

#### 禁止硬编码凭证
- 密码、API密钥等敏感信息不得直接写在代码中
- 必须从环境变量或安全配置中心读取

#### 加密规范
- 使用cryptography库进行加密操作
- 避免使用已废弃的加密算法

## 三、多线程与并发规范

### 3.1 线程安全
- 使用threading.Lock()保护共享数据
- 优先使用threading.local()存储线程本地数据

### 3.2 死锁预防
- 多个锁必须按固定顺序获取，避免循环等待
- 使用锁的超时参数，避免无限等待

**示例**：
```python
# 正确：固定顺序获取锁
with lock_a:
    with lock_b:
        # 临界区代码
        pass

# 错误：可能导致死锁
with lock_b:
    with lock_a:
        # 临界区代码
        pass
```

### 3.3 异步编程
- 使用async/await进行异步编程
- 避免在异步函数中使用阻塞操作
- 使用asyncio.gather()并发执行多个异步任务

## 四、性能规范

### 4.1 数据结构选择
- 列表操作使用列表推导式而非循环append
- 大量数据查找使用set而非list
- 频繁插入删除使用collections.deque

### 4.2 字符串操作
- 循环内字符串拼接使用join()方法
- 避免在循环中使用+操作符

**示例**：
```python
# 正确：使用join
result = ''.join(str(i) for i in range(1000))

# 错误：使用+操作符
result = ''
for i in range(1000):
    result += str(i)
```

### 4.3 资源管理
- 使用with语句管理文件、数据库连接等资源
- 及时释放大对象，避免内存泄漏

## 五、异常处理规范

### 5.1 异常捕获
- 禁止捕获Exception后不处理
- 按具体到一般顺序处理异常
- 记录日志并重新抛出

### 5.2 自定义异常
- 继承Exception创建业务异常
- 提供有意义的错误信息和错误代码

**示例**：
```python
class BusinessError(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
```

## 六、命名规范

### 6.1 类名
- 使用PascalCase（大驼峰）
- 名词或名词短语
- 具有描述性

**示例**：UserManager、OrderProcessor、DatabaseConnection

### 6.2 函数和变量名
- 使用snake_case（小写加下划线）
- 动词或动词短语
- 清晰表达功能

**示例**：process_order、find_user_by_id、is_valid

### 6.3 常量名
- 使用UPPER_SNAKE_CASE（大写加下划线）
- 有意义的名称

**示例**：MAX_CONNECTIONS、DEFAULT_TIMEOUT、API_BASE_URL

### 6.4 私有成员
- 私有属性和方法以单下划线开头
- 类私有成员以双下划线开头

**示例**：_internal_data、__private_method

## 七、导入规范

### 7.1 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入
4. 每组之间用空行分隔

### 7.2 导入方式
- 避免使用from module import *
- 使用相对导入时明确指定导入内容
- 长导入语句使用括号换行

**示例**：
```python
import os
import sys
from typing import List, Dict, Optional

import requests
import pandas as pd

from .models import User
from .utils import (
    process_data,
    validate_input
)
```