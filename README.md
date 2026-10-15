# 个人记账管理系统（Bookkeeping Management System）

玉切的个人记账管理系统：MySQL 8.0 数据库设计 + FastAPI 后端 + Vue 3 前端，全栈联调通过。

## 仓库结构

```
├── db/
│   └── schema.sql                 # 唯一建表脚本：users/accounts/categories/transactions
├── bookkeeping-api/               # 后端（FastAPI + SQLAlchemy 2.0 + Pydantic v2 + PyMySQL）
│   ├── app/                       #   分层：api / core / db / models / schemas / services
│   ├── scripts/                   #   冒烟测试、路由核对、服务探测、真实联调脚本
│   └── README.md                  #   接口文档、命名规范、设计决策（先读这个）
├── bookkeeping-web/               # 前端（Vue 3 + Vite + Element Plus + ECharts）
│   ├── src/                       #   页面 / API 封装 / 状态 / 工具
│   └── README.md                  #   目录结构、对接约定、联调记录
├── deploy/mysql/                  # 本地 MySQL 部署配置（Docker 与便携版两用，均脱敏）
├── archive/springboot/            # 历史归档：Spring Boot 版本后端（留档不维护）
├── LICENSE                        # MIT
└── README.md
```

## 快速开始

```bash
# 1. 数据库：本地便携版 MySQL（端口 3307）或 Docker，详见 deploy/mysql/README.md
#    建库：mysql -uroot -p < db/schema.sql

# 2. 后端（默认 8080）
cd bookkeeping-api
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
copy .env.example .env   # 填入 MYSQL_PASSWORD 等
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8080

# 3. 前端（默认 5173，与后端 CORS 白名单匹配）
cd bookkeeping-web
npm install
npm run dev
```

启动后访问 http://localhost:5173 ，注册账号即可使用；接口文档见 http://localhost:8080/docs。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 数据库 | MySQL 8.0（InnoDB / utf8mb4 / DECIMAL(15,2) 金额） |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic v2 + PyMySQL + python-jose + bcrypt |
| 前端 | Vue 3 + Vite + Element Plus + ECharts + Axios |
| 测试 | pytest 风格脚本（SQLite 内存库 49 项 + 真实 MySQL 联调 22 项 + 全流程 E2E） |

## 安全约定

- `.env` 含密码与 JWT 密钥，**已在 .gitignore 中排除，绝不入库**；仓库内只有 `.env.example` 模板。
- 金额全程使用字符串传递，避免浮点精度损失。
- 所有业务查询强制带 user_id，他人资源返回 404。

## 版本管理约定

- 分支：`main` 为主分支；功能开发使用 `feature/*` 分支，完成后合并。
- 提交信息遵循 Conventional Commits：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`。
- 里程碑打语义化标签（如 `v1.0.0`）。

## 文档索引

- 数据库设计说明与官方手册引用：见 `db/schema.sql` 头部注释
- 后端接口清单、命名规范、设计决策：`bookkeeping-api/README.md`
- 前端目录与对接约定：`bookkeeping-web/README.md`
- 本地 MySQL 部署（Docker / 便携版）：`deploy/mysql/README.md`

## License

MIT，见 [LICENSE](LICENSE)。
