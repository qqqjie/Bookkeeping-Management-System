# 微信云托管部署指南（bookkeeping-api）

本指南把 FastAPI 后端部署到微信云托管。所有关键规范均引自微信官方文档，文中标注了出处；
构建镜像未在本机实测（本机未安装 Docker），首次构建以云托管控制台日志为准。

## 一、前置条件

1. 小程序账号已注册（AppID 后续填入 `manifest.json`）；
2. 微信扫码登录微信云托管控制台（cloud.weixin.qq.com），选择你的小程序，按提示新建环境
   （环境ID 由平台生成，形如 `prod-1gxxxxxxxx`，后续 callContainer 要用）；
3. 在控制台「MySQL」页开通数据库：版本选 **8.0**（开通时选择是否大小写敏感，选定后不可修改；
   本项目的表名全小写，两种设置都兼容）。

## 二、初始化数据库

1. 控制台 MySQL → 数据库管理 → 新建数据库 `bookkeeping`；
2. 导入 `db/schema.sql`（建表 + 系统预设分类，Web 控制台支持 SQL 导入）；
3. 账号管理 → 新建专用账户：用户名 3-16 字符（字母开头）、主机填 `%`、
   权限限定 `bookkeeping` 库；密码 8-64 字符，须包含大小写字母、数字、符号中的任意三种
   （微信官方对云托管 MySQL 账号密码的规则）。

## 三、部署服务（二选一）

### 方式 A：本地上传 ZIP（最简单）

1. 本地打包上传包，包含四个条目：`Dockerfile`、`.dockerignore`、`requirements.txt`、`app/` 目录；
2. 云托管控制台 → 服务管理 → 新建服务（名称例如 `bookkeeping-api`；
   若小程序只用 callContainer 调用，可**不开启公网访问**以隔绝 DDoS，官方开发常识页明确
   “如果你只是在小程序或者公众号中 CallContainer 调用，可关闭公网访问”）；
3. 进入服务 → 版本与配置 → 新建版本 → 上传 ZIP → 等待自动构建（日志在控制台可查）；
4. 构建成功后「部署发布」。

### 方式 B：GitHub 流水线（推荐，代码已在 GitHub）

1. 服务 → 新建流水线 → 代码源授权 GitHub → 选择 `qqqjie/Bookkeeping-Management-System`；
2. 构建上下文目录填 `bookkeeping-api`（Dockerfile 所在目录）；
3. 触发构建 → 发布。私有仓库授权后即可拉取；国内访问 GitHub 不稳定时回退方式 A。

## 四、配置环境变量（服务 → 版本与配置 → 环境变量）

| 变量 | 值 | 说明 |
| --- | --- | --- |
| `MYSQL_HOST` | 云托管 MySQL **内网地址** | 控制台 MySQL 页复制；同一环境的服务与数据库天然内网互通，**不能用 localhost** |
| `MYSQL_PORT` | `3306` | |
| `MYSQL_USER` | 专用账户名 | 第二步创建 |
| `MYSQL_PASSWORD` | 专用账户密码 | |
| `MYSQL_DATABASE` | `bookkeeping` | |
| `JWT_SECRET` | 随机强密钥 | 用 `python -c "import secrets; print(secrets.token_hex(32))"` 生成 |
| `JWT_EXPIRE_HOURS` | `24` | |
| `CORS_ORIGINS` | 留空或前端域名 | 小程序走 callContainer 不经过浏览器、无需 CORS；留空表示禁止一切跨域 |

后端读取环境变量的逻辑见 `app/core/config.py`（pydantic-settings，大小写不敏感）。

## 五、验证部署

1. 服务详情页可见**默认公网域名**，形如 `https://{服务名}-{环境ID}.ap-shanghai.run.tcloudbase.com`
   （地域随环境，格式以控制台实际显示为准）；
2. 浏览器或 curl 访问 `https://你的默认域名/health`，应返回 `{"status":"ok"}`；
3. 官方明确提醒：**默认公网域名性能有限，仅能支持接口测试，请勿用于正式生产环境，
   且小程序后台无法配置使用默认公网域名**。因此默认域名只做连通性验证；
   小程序正式访问走 callContainer（见下）或自有已备案自定义域名。

## 六、小程序端对接（UniApp）

### 方式 1：wx.cloud.callContainer（官方推荐，免域名免备案）

```typescript
// App.vue 的 onLaunch 中初始化一次
// #ifdef MP-WEIXIN
wx.cloud.init({ env: '你的云托管环境ID' })
// #endif
```

```typescript
// 请求层传输示意（uni-app 的 src/api/request.ts 中按平台分流）
// #ifdef MP-WEIXIN
const res = await wx.cloud.callContainer({
  config: { env: '你的云托管环境ID' },
  path: '/api/v1/auth/login',          // 业务路径，根目录即 /
  method: 'POST',
  header: {
    'X-WX-SERVICE': '你的服务名',       // 云托管服务管理页中的服务名称
    'content-type': 'application/json',
    // JWT 继续走 Authorization 头，与现有 request.ts 逻辑一致
  },
  data: { loginId, password },
})
// callContainer 的返回结构以官方文档与联调打印为准，
// 把现有 {code, message, data} 信封解包逻辑接到返回体上即可
// #endif
```

官方限制（开发常识页核实）：小程序/公众号中 CallContainer **超时不得超过 15 秒**、
**请求大小限制 100K**；无需在小程序后台配置服务器域名。

### 方式 2：公网域名 + request 合法域名（H5 端或需要外部访问时）

1. 生产须绑定**自定义域名**（需 ICP 备案），默认域名不能配进小程序后台；
2. 小程序后台 → 开发管理 → 开发设置 → 服务器域名 → 配置 request 合法域名；
3. `src/api/request.ts` 的 `BASE_URL` 改为该域名，uni.request 链路不变；
4. 若 H5 端也要访问，把域名加进 `CORS_ORIGINS`。

## 七、已知注意事项（均来自官方文档）

1. **数据库自动暂停**：云托管 MySQL 默认 10 分钟无连接无 CPU 使用即暂停，
   冷启动期间请求可能报 `CynosDB serverless instance is resuming`。
   个人项目建议在数据库设置中关闭自动暂停（持续产生 0.25 CCU 最小算力费用），
   或在代码中对该报错加重试。当前后端无重试逻辑。
2. **服务冷启动**：最小副本为 0 时，半小时无请求缩容到 0，下次请求有冷启动耗时。
   不能接受冷启动就在服务设置中把实例副本数最小值设为 1。
3. **容器无持久化存储**：勿把文件写进容器，扩缩容/重启会还原；需要存文件用对象存储。
4. **本地 MySQL 不可达**：本机 D 盘便携版 MySQL（3307）在云端容器里无法访问，
   必须使用云托管 MySQL 内网地址（或同 VPC 的腾讯云 MySQL）。
5. **规格**：默认 CPU 0.5 核 / 内存 1G；偶发 500 或请求慢时先看容器 CPU/内存使用率再升规格。

## 八、本地构建命令（本机装有 Docker 时自测用）

```bash
cd "D:/WorkBuddyCache/Bookkeeping Management System/bookkeeping-api"
docker build -t bookkeeping-api:local .
docker run --rm -p 9000:8080 -e MYSQL_HOST=你的数据库地址 bookkeeping-api:local
# 容器内硬编码监听 8080（非 root 用户无法绑定 80），本地映射宿主 9000 → 容器 8080
# 本机未安装 Docker，以上命令未经实测；镜像验证以云托管构建日志为准。
```
