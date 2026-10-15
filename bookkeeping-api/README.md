# bookkeeping-api · 个人记账管理系统后端（FastAPI）

基于 `../db/schema.sql`（users / accounts / categories / transactions 四张表）实现的 RESTful API。
本目录是 Python 技术栈版本；此前的 Spring Boot 版本已归档至 `../archive/springboot/`。

## 一、技术栈与实测版本

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| FastAPI | 0.143.1 | Web 框架，自带 Swagger 文档（/docs） |
| SQLAlchemy | 2.1.4 | ORM，2.0 声明式 API（Mapped / mapped_column） |
| Pydantic | 2.14.1 | 请求校验与响应序列化（v2） |
| PyMySQL | 1.2.3 | MySQL 驱动（纯 Python） |
| python-jose[cryptography] | 3.5.0 | JWT 签发与校验 |
| bcrypt | 5.0.0 | 密码哈希 |
| uvicorn | 0.54.0 | ASGI 服务器 |
| pydantic-settings | 2.16.0 | 配置管理（.env） |

版本均为本机安装实测（2026-10-15）。

**关于 passlib 的偏差（可验证事实）**：原始技术栈需求指定 `passlib[bcrypt]`。
passlib 1.7.4 是 2020 年最后一版，其 bcrypt 后端在初始化自检
（`detect_wrap_bug`）时会调用 `bcrypt.hashpw` 并传入超过 72 字节的测试口令，
bcrypt 4.1 及以上版本对此直接抛出 `ValueError`，导致哈希失败；而 bcrypt 4.0.1
没有 Python 3.13/3.14 的预编译 wheel（源码构建需要 Rust 工具链）。
因此 `app/core/security.py` 直接使用 bcrypt 5.x（同一算法的上游实现），
对外接口 `hash_password` / `verify_password` 不变，安全强度相同。

**关于 python-jose 的安全说明**：CVE-2024-33663（算法混淆）影响 3.4.0 以下版本，
GitHub Advisory 编号 GHSA-6c5p-j8vq-pqhj；本项目固定 3.5.0（已含修复），
且 `decode_access_token` 显式限定 `algorithms=["HS256"]`。

## 二、快速开始

环境要求：Python 3.10+（本机验证用 3.13；你的系统 Python 3.14 亦可）。

```bash
# 1. 建库建表（MySQL 中执行仓库根目录的 SQL）
mysql -uroot -p < ../db/schema.sql

# 2. 创建虚拟环境并安装依赖
cd bookkeeping-api
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows；Linux/macOS 用 .venv/bin/pip

# 3. 配置环境变量
copy .env.example .env    # Windows；然后编辑 .env 填入 MySQL 密码与 JWT 密钥

# 4. 启动
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8080
```

启动后：

- 接口基地址：`http://localhost:8080/api/v1`
- Swagger 交互式文档：`http://localhost:8080/docs`
- 健康检查：`http://localhost:8080/health`

本机无系统 Python 3.13 时的等价命令（IntelliJ 自带 JBR 不含 pip，需用管理版 venv）：

```bash
/c/Users/JieNeSy/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m uvicorn app.main:app --port 8080
```

## 三、目录结构

```
bookkeeping-api/
├── app/
│   ├── main.py               # 应用装配：CORS、路由、异常处理
│   ├── api/                  # 路由层（6 个 router）+ deps.py（get_db / get_current_user）
│   ├── core/                 # config / errors / responses / security / money / dates
│   ├── db/                   # base（DeclarativeBase）/ session（engine / get_db）
│   ├── models/               # SQLAlchemy 模型（4 表）+ 3 个枚举
│   ├── schemas/              # Pydantic v2 请求/响应模型（camelCase 别名）
│   └── services/             # 业务逻辑（6 个模块）
├── scripts/
│   ├── smoke_test.py         # 端到端冒烟测试（SQLite 内存库，49 项断言）
│   ├── check_routes.py       # 打印全部已注册路由
│   └── check_server.py       # 启动 uvicorn 并探测 /health、/openapi.json、/docs
├── requirements.txt
├── .env.example
└── README.md
```

## 四、命名规范

1. **包/模块**：小写 snake_case，按职责分层（api / core / db / models / schemas / services）。
2. **模型类**：大驼峰，与表名对应（`users` → `User`）；枚举类即类型名（`AccountType`）。
3. **Schema 类**：请求以 `XxxSaveRequest` / `XxxUpdateRequest` 结尾，响应以 `VO` 结尾。
4. **函数**：snake_case、动词开头（`create_account` / `list_transactions` / `get_balance`）。
5. **私有辅助**：下划线前缀（`_get_owned` / `_validate_references`）。
6. **JSON 字段**：统一 camelCase（由 `alias_generator=to_camel` 生成），与 Spring Boot 版一致。
7. **REST**：复数资源名词 + HTTP 动词；版本前缀 `/api/v1`；他人资源返回 404 不暴露存在性。
8. **常量**：模块级全大写下划线（如 `_BCRYPT_MAX_BYTES`）。

## 五、API 清单（23 个端点）

除注册/登录外均需请求头 `Authorization: Bearer <token>`。成功响应统一为
`{"code":200,"message":"操作成功","data":...}`；失败时 HTTP 状态码与 body.code 一致。

### 认证与用户（4）

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| POST | /api/v1/auth/register | 注册，成功直接返回 token 与用户信息 |
| POST | /api/v1/auth/login | 登录，loginId 支持用户名或邮箱 |
| GET | /api/v1/users/me | 当前登录用户信息 |
| PUT | /api/v1/users/me | 修改昵称/邮箱 |

### 账户（6）

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| POST | /api/v1/accounts | 新增账户（重名 409） |
| GET | /api/v1/accounts | 启用中账户列表，含实时余额 |
| GET | /api/v1/accounts/{accountId} | 账户详情 |
| GET | /api/v1/accounts/{accountId}/balance | 单账户实时余额 |
| PUT | /api/v1/accounts/{accountId} | 全量更新 |
| DELETE | /api/v1/accounts/{accountId} | 删除（有流水 409） |

### 分类（5）

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| POST | /api/v1/categories | 新增分类，parentId 可空支持二级 |
| GET | /api/v1/categories | 系统预设 + 用户自定义合并，按 sort_order 排序 |
| GET | /api/v1/categories/{categoryId} | 分类详情 |
| PUT | /api/v1/categories/{categoryId} | 更新 |
| DELETE | /api/v1/categories/{categoryId} | 删除（有子分类或流水 409） |

### 交易（5）

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| POST | /api/v1/transactions | 记一笔收入/支出 |
| GET | /api/v1/transactions | 分页查询；支持 month/type/accountId/categoryId/startTime/endTime 筛选，按交易时间倒序 |
| GET | /api/v1/transactions/{transactionId} | 流水详情 |
| PUT | /api/v1/transactions/{transactionId} | 更新 |
| DELETE | /api/v1/transactions/{transactionId} | 删除 |

### 统计（3，本次新增）

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| GET | /api/v1/stats/monthly-summary?month=2026-10 | 月度收支汇总：收入/支出/净额/笔数（month 缺省为当月） |
| GET | /api/v1/stats/category-share?month=2026-10&type=expense | 分类占比：各分类金额与百分比，按金额降序 |
| GET | /api/v1/stats/trend?months=6 | 近 N 个月收支趋势（1-12，默认 6，按月份升序，无数据月份补零） |

注册示例：

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"yuqie","email":"yuqie@example.com","password":"abc12345","nickname":"玉切"}'
```

查询本月支出分类占比：

```bash
curl "http://localhost:8080/api/v1/stats/category-share?month=2026-10&transactionType=expense" \
  -H "Authorization: Bearer <token>"
```

## 六、测试步骤

```bash
# 1. 端到端冒烟测试（SQLite 内存库，不需要 MySQL；49 项断言）
PYTHONPATH=. python scripts/smoke_test.py

# 2. 路由清单核对
PYTHONPATH=. python scripts/check_routes.py

# 3. 真实启动探测（health / openapi / docs）
PYTHONPATH=. python scripts/check_server.py

# 4. 真实 MySQL 联调（需先按第九节启动本地 MySQL；17 项断言）
PYTHONPATH=. python scripts/live_test.py
```

冒烟测试覆盖：注册/登录/令牌、账户 CRUD 与实时余额、分类合并与二级分类、
交易筛选/分页/倒序、三个统计接口的数值正确性、越权隔离（他人资源 404）、
删除保护（外键冲突 409）、各更新流程。本机实测结果：**49 通过，0 失败**。

## 七、设计决策（主观判断，附理由）

1. **金额全程 Decimal**：模型 `Numeric(15,2)`、请求 `Decimal`、响应序列化为字符串
   （如 `"35.50"`）。FastAPI 默认会把 Decimal 序列化成 JSON 浮点数而损失精度，
   故在 VO 层统一转为字符串。
2. **统一响应信封**：保留 Spring Boot 版的 `{code, message, data}` 结构与错误码，
   HTTP 状态码同步（400/401/404/409/500）。
3. **数据隔离**：所有业务函数以 `user_id` 为第一参数，所有权校验失败一律 404；
   系统分类（user_id IS NULL）对所有用户可见但不可改不可删。
4. **删除语义**：账户/分类为物理删除，被流水引用时由 MySQL 外键 RESTRICT 拒绝，
   服务层捕获 `IntegrityError` 转 409；流水删除即时反映到实时余额。
5. **趋势查询用 Python 分桶**：按自然月分组在 MySQL 需 `DATE_FORMAT`（方言相关），
   个人记账数据量下按行取回后分桶完全够用，且保持 SQL 可移植（测试可在 SQLite 运行）。
6. **主键类型**：`BigInteger.with_variant(Integer, "sqlite")`，MySQL 上仍是 BIGINT
   （对应 schema.sql），SQLite 上渲染为 INTEGER 以获得自增别名（仅测试用途）。
7. **时间戳由应用层填充**：`created_at` / `updated_at` 用 Python 默认值写入，
   与 schema 的 `DEFAULT CURRENT_TIMESTAMP` / `ON UPDATE` 不冲突（应用总是显式传值）。

## 八、已知限制

- 未做转账类型（双账户互转）、预算表、标签、多账套、多币种。
- JWT 无刷新令牌与登出黑名单；登录无速率限制。
- 未引入 Alembic，schema 变更仍由 `../db/schema.sql` 单一管理。
- 尚未连接真实 MySQL 跑通（缺 root 密码）；联调步骤见下文。

## 九、本地 MySQL 部署与真实连接测试（已完成）

本机未安装 Docker，改用**便携版 MySQL**（官方 ZIP 解压，不注册系统服务，全部文件在 D 盘）：

| 项 | 值 |
| --- | --- |
| 程序目录 | `D:\bookkeeping-mysql\server`（mysql-8.0.44-winx64.zip 解压，ZIP 保留在同目录） |
| 数据目录 | `D:\bookkeeping-mysql\data` |
| 配置文件 | `D:\bookkeeping-mysql\my.ini` |
| 端口 | 3307（避开现有 MySQL80 的 3306，两个实例互不影响） |
| root 密码 | 见本地 `.env` 与部署目录（仓库中不保存任何密码） |
| 应用账户 | bookkeeping_app（密码见本地 `.env`，仅授权 bookkeeping 库） |

日常操作：

```bash
# 启动（保持窗口运行）
D:\bookkeeping-mysql\server\bin\mysqld.exe --defaults-file=D:\bookkeeping-mysql\my.ini

# 连接（密码见本地 .env / 部署说明）
D:\bookkeeping-mysql\server\bin\mysql.exe --defaults-file=D:\bookkeeping-mysql\my.ini -uroot -p

# 优雅停止
D:\bookkeeping-mysql\server\bin\mysqladmin.exe --defaults-file=D:\bookkeeping-mysql\my.ini -uroot -p shutdown
```

Docker 方案（备用）：`D:\bookkeeping-mysql\docker-compose.yml` 已按 3307 端口备好，
将来安装 Docker 后执行 `cd D:\bookkeeping-mysql && docker compose up -d` 即可，
`init/01-schema.sql` 会在容器首次初始化时自动执行。

真实连接测试（**已通过，17/17**）：

```bash
PYTHONPATH=. python scripts/live_test.py
```

该脚本先以 bookkeeping_app 账户直连数据库校验版本与表结构，再自动启动 FastAPI，
依次走完 注册 → 登录 → 建账户 → 记支出/收入 → 查余额 → 月度汇总/分类占比/趋势 → 清理测试数据。
