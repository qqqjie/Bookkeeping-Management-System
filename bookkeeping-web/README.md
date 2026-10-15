# bookkeeping-web · 个人记账管理系统前端

Vue 3 + Vite + Element Plus + ECharts，对接 `../bookkeeping-api`（FastAPI 后端）。

## 技术栈与关键依赖

| 依赖 | 版本范围 | 用途 |
| --- | --- | --- |
| vue | ^3.5 | 框架 |
| vue-router | ^4.5 | 路由（含登录守卫） |
| element-plus | ^2.9 | 组件库（中文语言包） |
| @element-plus/icons-vue | ^2.3 | 图标 |
| echarts | ^5.6 | 饼图 / 折线图 |
| axios | ^1.7 | HTTP 客户端 |
| vite | ^5.4 | 构建与开发服务器（5173） |

版本以 `npm install` 实际解析为准（见 package-lock.json）。

## 目录结构

```
bookkeeping-web/
├── index.html
├── vite.config.js            # 5173 端口、@ 别名指向 src
├── package.json
└── src/
    ├── main.js               # 应用装配（Element Plus 中文、图标、路由）
    ├── App.vue
    ├── router/index.js       # 路由 + 未登录跳转守卫
    ├── api/
    │   ├── request.js        # axios 实例：统一解包 {code,message,data}、401 跳登录、自动带 JWT
    │   ├── auth.js / accounts.js / categories.js / transactions.js / stats.js
    ├── stores/auth.js        # 登录态（token + user，localStorage 持久化）
    ├── utils/format.js       # 金额两位小数、日期、百分比格式化
    ├── styles/index.css      # 全局样式（收入红/支出绿的财务配色）
    ├── layouts/MainLayout.vue      # 侧边栏导航 + 顶部用户信息 + 退出登录
    └── views/
        ├── LoginView.vue           # 登录/注册（表单校验规则与后端一致）
        ├── DashboardView.vue       # 本月收支卡片 + 分类占比饼图 + 近 6 个月趋势
        ├── TransactionsView.vue    # 流水：筛选/分页/新增/编辑/删除弹窗
        ├── AccountsView.vue        # 账户管理（含实时余额列）
        └── CategoriesView.vue      # 分类管理（系统预设只读、自定义可维护）
```

## 开发与构建

```bash
# 安装依赖（npm 缓存已重定向到 D 盘）
npm install

# 开发服务器（http://localhost:5173，与后端 CORS 白名单匹配）
npm run dev

# 生产构建
npm run build
```

## 对接约定

1. **接口基地址**：`http://localhost:8080/api/v1`（`src/api/request.js`）。
2. **统一响应**：拦截器解包 `{code, message, data}`，业务码非 200 时弹出 `message` 并 reject；401 时清空登录态并跳转 `/login`。
3. **JWT**：登录/注册返回的 token 存入 localStorage，后续请求自动携带 `Authorization: Bearer <token>`。
4. **金额精度**：后端全程返回字符串（如 `"6964.51"`），前端不做数值运算，仅展示时保留两位小数；提交时同样以字符串发送。
5. **退出登录**：前端清除 token 与用户信息后跳转登录页（后端无状态，无需调用接口）。
6. **数据隔离**：所有列表均由后端按当前用户过滤，前端不传递 user_id。

## 联调前置

1. 后端已启动：`cd ../bookkeeping-api && python -m uvicorn app.main:app --port 8080`。
2. MySQL 已就绪（便携版实例，端口 3307，详见 `../bookkeeping-api/README.md` 第九节）。
3. 浏览器访问 http://localhost:5173 ，注册账号即可开始使用。

## 联调验证记录（2026-10-15）

- `vite build` 构建通过；dev 服务器下 `/src/main.js`、`/src/views/DashboardView.vue`、`/src/api/request.js` 均编译正常。
- CORS 预检通过：`OPTIONS` 返回 `Access-Control-Allow-Origin: http://localhost:5173`、放行 `content-type,authorization` 头与全部 REST 方法、`Allow-Credentials: true`。
- 后端侧全流程脚本（注册→登录→建账户→记账→余额/列表/统计→退出→清理）**22/22 通过**：`cd ../bookkeeping-api && python scripts/e2e_running.py`。
- 浏览器级点击验证未执行：本机网络策略阻断 Chromium 下载（storage.googleapis.com 不可达），你可在真实浏览器中手动走一遍上述流程。
