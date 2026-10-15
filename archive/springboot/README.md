# bookkeeping-api · 个人记账管理系统 RESTful API

基于 `../db/schema.sql`（users / accounts / categories / transactions 四张表）实现的后端服务，
覆盖用户注册登录、账户 / 分类 / 交易流水的增删改查。

## 一、技术栈与版本

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| Spring Boot | 3.5.16 | 3.5 线最终 OSS 补丁版（2026-06-25 发布）；业务代码与 4.x 通用，升级只需改 pom 版本号 |
| Spring Framework | 6.2.x | 随 Spring Boot 3.5.16 管理 |
| MyBatis-Plus | 3.5.17 | 2026-07-08 发布的当前最新版；分页插件需搭配 mybatis-plus-jsqlparser（见下方说明） |
| jjwt | 0.12.6 | JWT 签发与校验 |
| MySQL | 8.0.44 | 本机已装（服务 MySQL80，端口 3306） |
| JDK | 17+ | 本机可用 IntelliJ 自带 JBR 21.0.9 |

版本说明（可验证事实）：Spring Boot 当前最新线为 4.1.1（2026-08-20 发布），3.5 线已于 2026-06-30
结束 OSS 支持。本项目选 3.5.16 的原因是 3.x API 稳定、生态成熟、与 MyBatis-Plus 完全兼容；
教学场景下两者差异不影响学习，升级 4.x 时仅需调整 pom 中的 parent 版本号。

关于 MyBatis-Plus 版本（已通过 jar 包内容与官方文档双向核实的事实）：自 v3.5.9 起，
`PaginationInnerInterceptor` 被拆分为独立组件 `mybatis-plus-jsqlparser`，官方文档原话为
"Starting from v3.5.9, PaginationInnerInterceptor has been separated out. If you need to use it,
you must separately introduce the mybatis-plus-jsqlparser dependency."
本项目因此固定 `mybatis-plus.version = 3.5.17` 并显式引入 `mybatis-plus-jsqlparser`，
`MybatisPlusConfig` 中仍使用经典的 `new PaginationInnerInterceptor(DbType.MYSQL)` 写法，
import 路径未变（`com.baomidou.mybatisplus.extension.plugins.inner`）。

## 二、环境要求

- JDK 17 或更高版本
- Maven 3.6+
- MySQL 8.0（数据库名 `bookkeeping`）

本机零安装启动方式（已验证可行）：

```bash
# IntelliJ 自带 JBR 21 即满足 JDK 17+ 要求
"/d/Program Files/JetBrains/IntelliJ IDEA Community Edition 2025.2.5/jbr/bin/java.exe" -version

# IntelliJ 自带 Maven 3，无需单独安装
"/d/Program Files/JetBrains/IntelliJ IDEA Community Edition 2025.2.5/plugins/maven/lib/maven3/bin/mvn" -version
```

## 三、快速开始

1. 建库建表（在 MySQL 中执行仓库根目录的 SQL）：

```bash
mysql -uroot -p < ../db/schema.sql
```

2. 配置数据库密码。服务从环境变量读取密码，避免明文入库：

```bash
# bash
export MYSQL_PASSWORD='你的 root 密码'
# 或在 IDEA 运行配置的 Environment variables 中添加 MYSQL_PASSWORD=你的root密码
```

3. 编译运行：

```bash
export JAVA_HOME="/d/Program Files/JetBrains/IntelliJ IDEA Community Edition 2025.2.5/jbr"
MVN="/d/Program Files/JetBrains/IntelliJ IDEA Community Edition 2025.2.5/plugins/maven/lib/maven3/bin/mvn"

$MVN spring-boot:run
```

服务启动后监听 `http://localhost:8080`。

4. 或在 IntelliJ IDEA 中直接打开本目录：IDEA 会自动识别 Maven 项目，
   Project SDK 选择自带的 JBR 21 即可运行。

## 四、目录结构与命名规范

```
bookkeeping-api/
├── pom.xml
└── src/main/
    ├── java/com/bookkeeping/
    │   ├── BookkeepingApplication.java     启动类
    │   ├── common/                         Result 统一响应、PageVO 分页视图
    │   ├── config/                         MybatisPlusConfig（分页拦截器、时间字段自动填充）
    │   ├── controller/                     XxxController，REST 接口层
    │   ├── dto/                            XxxRequest 请求体、XxxResponse 响应体
    │   ├── entity/                         Xxx 实体，与表一一对应
    │   ├── enums/                          AccountType / CategoryType / TransactionType
    │   ├── exception/                      BusinessException、ErrorCode、GlobalExceptionHandler
    │   ├── mapper/                         XxxMapper，MyBatis-Plus 数据访问层
    │   ├── security/                       JWT 与 Spring Security 配置
    │   ├── service/                        XxxService 接口 + impl/XxxServiceImpl 实现
    │   └── vo/                             XxxVO 对外视图对象
    └── resources/
        └── application.yml
```

命名规范（本项目强制执行）：

1. **包名**：全部小写、点分分隔，按技术分层划分：`com.bookkeeping.{controller,service,mapper,entity,dto,vo,enums,security,config,common,exception}`。
2. **类名**：大驼峰。Controller 以 `XxxController` 结尾，Service 接口以 `XxxService` 结尾、实现类以 `XxxServiceImpl` 结尾，Mapper 以 `XxxMapper` 结尾，实体即表名的大驼峰形式（`users` → `User`）。
3. **方法名**：小驼峰、动词开头。查询用 `getById` / `listByXxx` / `existsByXxx` 前缀，新增用 `create`，修改用 `update`，删除用 `delete`。
4. **变量与参数**：小驼峰；布尔语义字段用 `is/has/can` 之外的完整动宾结构（如 `includeInTotal`）。
5. **常量**：全大写下划线（如 `STATUS_ACTIVE`）。
6. **数据库 ↔ Java**：数据库字段用下划线 snake_case，Java 属性用小驼峰，映射由 `map-underscore-to-camel-case: true` 自动完成，禁止手写别名绕开。
7. **REST 路径**：资源用复数名词（`/api/v1/accounts`），路径段全小写可用连字符，动作由 HTTP 方法表达，版本号放在路径前缀。
8. **JSON 字段**：小驼峰；枚举序列化为数据库字面量（`income` / `expense` / `cash`）。
9. **异常**：业务错误一律抛 `BusinessException(ErrorCode)`，由 `GlobalExceptionHandler` 统一收口，禁止在 Controller 里 try-catch 后返回 null。

## 五、接口一览

所有接口统一响应体为 `{"code":200,"message":"...","data":...}`。
除注册 / 登录外，所有接口都要求在请求头携带 `Authorization: Bearer <token>`。

### 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /api/v1/auth/register | 注册（username、email、password、nickname 可选），成功直接返回 token |
| POST | /api/v1/auth/login | 登录，loginId 支持用户名或邮箱 |

### 用户

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /api/v1/users/me | 查看当前登录用户信息 |
| PUT | /api/v1/users/me | 修改当前用户昵称 / 邮箱 |

### 账户

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /api/v1/accounts | 新增账户 |
| GET | /api/v1/accounts | 当前用户的启用中账户列表（含实时余额） |
| GET | /api/v1/accounts/{accountId} | 账户详情 |
| GET | /api/v1/accounts/{accountId}/balance | 单账户实时余额 |
| PUT | /api/v1/accounts/{accountId} | 全量更新账户 |
| DELETE | /api/v1/accounts/{accountId} | 删除账户（有流水时返回 409） |

### 分类

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /api/v1/categories | 新增分类（parentId 可空，支持二级） |
| GET | /api/v1/categories | 当前用户分类 + 系统预设分类 |
| GET | /api/v1/categories/{categoryId} | 分类详情 |
| PUT | /api/v1/categories/{categoryId} | 更新分类 |
| DELETE | /api/v1/categories/{categoryId} | 删除分类（有子分类或流水时返回 409） |

### 交易流水

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /api/v1/transactions | 记一笔收入或支出 |
| GET | /api/v1/transactions | 分页查询，支持 accountId / categoryId / type / startTime / endTime 过滤 |
| GET | /api/v1/transactions/{transactionId} | 流水详情 |
| PUT | /api/v1/transactions/{transactionId} | 更新流水 |
| DELETE | /api/v1/transactions/{transactionId} | 删除流水 |

注册请求示例：

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"yuqie","email":"yuqie@example.com","password":"abc12345","nickname":"玉切"}'
```

记一笔支出示例：

```bash
curl -X POST http://localhost:8080/api/v1/transactions \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"accountId":1,"categoryId":1,"transactionType":"expense","amount":"35.50","transactionTime":"2026-10-15T12:30:00","remark":"午饭"}'
```

## 六、设计决策（主观判断，附理由）

1. **余额不落库**：`currentBalance` 由 `initial_balance + 收入合计 - 支出合计` 实时计算，
   与 schema.sql 的设计约定一致，避免双写不一致。
2. **物理删除 + 外键保护**：DELETE 为物理删除，账户 / 分类被流水引用时由数据库外键
   RESTRICT 拒绝，服务层捕获后转换为 409，保证金融记录不被静默丢弃。
3. **停用与删除分离**：`status` 字段表示停用 / 启用，是独立于删除的状态操作；
   列表接口默认只返回 `status = 1` 的记录。
4. **他人资源返回 404 而非 403**：避免泄露资源是否存在。
5. **金额恒为正数**：方向由 `transactionType` 决定，与 schema 的 `CHECK (amount > 0)` 对应。
6. **交易时间与录入时间分离**：`transactionTime` 记录业务发生时间，`createdAt` 记录录入时间。
7. **枚举双向字面量映射**：`@EnumValue` 负责数据库读写，`@JsonValue` / `@JsonCreator` 负责 JSON，
   接口层只见 `income` / `expense` / `cash` 这类字面量，不见 `INCOME` 这类 Java 常量名。

## 七、错误码

| code | 含义 | 触发场景 |
| --- | --- | --- |
| 200 | 操作成功 | 正常响应 |
| 400 | 请求参数不合法 | 参数校验失败 |
| 401 | 未登录或登录已过期 | 未携带 / 携带无效 token，密码错误 |
| 403 | 无权限 | 已登录但角色不足 |
| 404 | 资源不存在 | 访问不存在或不属于当前用户的资源 |
| 409 | 数据冲突 | 用户名 / 邮箱 / 账户名 / 分类名重复，删除被引用数据 |
| 500 | 服务器内部错误 | 未捕获异常 |

## 八、已知限制与后续扩展

- 未做转账类型（双账户互转）、预算表、标签、多账套、多币种，这些在 schema 设计时已预留讨论空间。
- JWT 为单令牌模式，无刷新令牌与登出黑名单；生产环境应补充。
- SQL 日志默认开启（`log-impl: StdoutImpl`），生产环境应关闭。
- MyBatis-Plus 3.5.9+ 的分页插件位于独立组件 `mybatis-plus-jsqlparser` 中，本项目已在 pom 中固定该依赖；
  卸载或降级 MyBatis-Plus 时需同步处理这个依赖，否则 `MybatisPlusConfig` 无法编译。
