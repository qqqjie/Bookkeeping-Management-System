# 本地 MySQL 部署配置

两套方案共用同一份 schema（`../../db/schema.sql`），端口均为 **3307**（避开本机现有 MySQL80 的 3306）。

> 安全约定：本目录所有文件均**不含明文密码**。Docker 方案通过 `MYSQL_ROOT_PASSWORD` 环境变量注入；
> 便携版方案的密码只存在于本机 `.env` 与 `my.ini` 同级的部署目录中，不进仓库。

## 方案一：便携版 MySQL（当前本机使用）

程序解压于 `D:\bookkeeping-mysql\server`（mysql-8.0.44-winx64.zip），数据目录 `D:\bookkeeping-mysql\data`，
未注册 Windows 服务，以普通进程运行：

```bash
# 启动
D:\bookkeeping-mysql\server\bin\mysqld.exe --defaults-file=D:\bookkeeping-mysql\my.ini

# 建库建表（首次）
D:\bookkeeping-mysql\server\bin\mysql.exe --defaults-file=D:\bookkeeping-mysql\my.ini -uroot -p < ../../db/schema.sql

# 创建应用专用账户（先替换 app_user.sql 中的密码占位符）
D:\bookkeeping-mysql\server\bin\mysql.exe --defaults-file=D:\bookkeeping-mysql\my.ini -uroot -p < app_user.sql

# 停止
D:\bookkeeping-mysql\server\bin\mysqladmin.exe --defaults-file=D:\bookkeeping-mysql\my.ini -uroot -p shutdown
```

`my.ini` 为本机便携版配置的副本（路径写死了 D 盘，换机器需调整 basedir/datadir）。

## 方案二：Docker（备用）

```bash
# 1. 设置密码环境变量
export MYSQL_ROOT_PASSWORD='你的强密码'        # Git Bash
# PowerShell: $env:MYSQL_ROOT_PASSWORD='你的强密码'

# 2. 将 schema.sql 放到初始化目录（容器首次启动自动执行）
mkdir -p /d/bookkeeping-mysql/init
cp ../../db/schema.sql /d/bookkeeping-mysql/init/01-schema.sql

# 3. 启动
cd D:/bookkeeping-mysql && docker compose up -d

# 4. 创建应用账户（替换密码后执行）
docker exec -i bookkeeping-mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" < app_user.sql
```

## 账户与权限

| 账户 | 用途 | 权限 |
| --- | --- | --- |
| root | 运维、建库、执行 schema | 全部（生产环境应限制来源） |
| bookkeeping_app | 后端服务连接 | 仅 `bookkeeping` 库全部权限 |

后端 `.env` 中固定使用 `bookkeeping_app` 连接，遵循最小权限原则。
