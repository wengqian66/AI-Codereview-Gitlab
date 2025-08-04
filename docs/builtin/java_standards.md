# Java编码规范

**Java代码规范 | Java编程标准 | Java最佳实践 | Java代码审查**

Java编程语言的编码规范和最佳实践指南，适用于代码审查和质量控制。

---

## 一、代码质量规范

### 1.1 可读性与维护性

#### 禁止重复代码
- 同一段代码在多个地方重复出现时，必须提取为公共方法或工具类
- 遵循DRY（Don't Repeat Yourself）原则

#### 方法复杂度限制
- 单个方法的圈复杂度（分支数）不得超过10，否则需拆分子方法
- 使用工具检测圈复杂度，如SonarQube

#### 清除无效代码
- 注释掉的代码必须删除
- 未使用的私有方法（UnusedPrivateMethod）必须删除

#### 避免冗余操作
- 禁止不必要的自动装箱/拆箱（如Integer.valueOf(i)直接改用int）

### 1.2 面向对象设计

#### 序列化规范
- 所有Serializable类必须显式定义serialVersionUID（S2057）

#### 静态内部类
- 如果内部类不访问外部类成员，必须声明为static（S2694）

#### 方法重写
- 重写父类方法时必须添加@Override注解（S2699）

## 二、安全规范

### 2.1 输入与输出安全

#### SQL注入防护
- 禁止拼接SQL语句（SQL_INJECTION）
- 必须使用预编译（PreparedStatement）或ORM框架参数化查询

#### 路径遍历防护
- 用户提供的文件路径必须校验合法性
- 禁止直接拼接（PATH_TRAVERSAL_IN）

#### XXE防护
- XML解析器（如SAXParser）必须禁用外部实体（XXE_SAXPARSER）

### 2.2 敏感信息保护

#### 禁止硬编码凭证
- 密码、API密钥等敏感信息不得直接写在代码中（HARD_CODE_PASSWORD）
- 必须从安全配置中心读取

#### 加密规范
- 使用AES、RSA等算法时，密钥长度需符合安全标准
- RSA至少2048位（RSA_KEY_SIZE）

## 三、多线程与并发规范

### 3.1 同步锁使用
- 禁止在同步块内调用sleep()或wait()（SWL_SLEEP_WITH_LOCK_HELD）

### 3.2 线程通知
- 多线程通信时优先使用notifyAll()，而非notify()（NO_NOTIFY_NOT_NOTIFYALL）

### 3.3 线程池管理
- 禁止直接创建线程（DM_USELESS_THREAD）
- 必须使用线程池

## 四、性能规范

### 4.1 集合初始化
- 初始化ArrayList、HashMap等集合时，必须指定初始容量（PSC_SUBOPTIMAL_COLLECTION_SIZING）

### 4.2 字符串操作
- 循环内字符串拼接必须使用StringBuilder（ISB_INEFFICIENT_STRING_BUFFERING）

### 4.3 资源释放
- 所有IO流、数据库连接必须显式关闭（S2093）
- 推荐使用try-with-resources

## 五、异常处理规范

### 5.1 异常捕获
- 禁止捕获Exception后不处理（S1181）
- 需记录日志或向上抛出

### 5.2 自定义异常
- 避免直接抛出RuntimeException
- 应定义业务异常类（S112）

## 六、测试规范

### 6.1 单元测试有效性
- 失败的单元测试必须修复（FailedUnitTests）
- 禁止忽略

### 6.2 测试覆盖率
- 核心业务代码行覆盖率不低于80%
- 需配合SonarQube配置

## 七、其他关键规则

### 7.1 Switch语句
- 必须包含default分支（SwitchLastCaseIsDefaultCheck）

### 7.2 日期处理
- 禁止使用SimpleDateFormat作为静态变量（STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE）
- SimpleDateFormat线程不安全

### 7.3 随机数安全
- 生成随机数必须用SecureRandom，而非Random（PREDICTABLE_RANDOM）

## 八、命名规范

### 8.1 类名
- 使用PascalCase（大驼峰）
- 名词或名词短语
- 具有描述性

**示例**：UserManager、OrderProcessor、DatabaseConnection

### 8.2 方法名
- 使用camelCase（小驼峰）
- 动词或动词短语
- 清晰表达功能

**示例**：processOrder、findUserById、isValid

### 8.3 变量名
- 使用camelCase
- 有意义的名称
- 避免单字母（除循环计数器外）

**示例**：firstName、itemCount、isActive

## 九、类设计原则

### 9.1 单一职责原则
- 每个类只负责一个功能领域
- 避免承担多个不相关的职责

**好的设计**：UserService专注用户管理
**避免**：一个类处理用户、邮件、加密等多个职责

### 9.2 封装
- 使用私有字段和公共方法
- 隐藏内部实现，提供清晰接口

**示例**：BankAccount类私有balance字段，公共deposit/withdraw方法