# 个人记账管理系统 - 微信云托管部署镜像
#
# 构建上下文：bookkeeping-api/ 目录（与 requirements.txt、app/ 同级）
#
# 端口说明（2026-10-16 按实际部署日志修正）：
#   容器内 USER appuser 为非 root 用户，无法绑定 1024 以下的特权端口（80），
#   且本环境存活探针探测的是 8080；因此硬编码监听 8080，不再依赖 PORT 环境变量。
#   发布表单的“端口”字段须与容器监听端口一致，填 8080。
# 微信云托管其他规范（官方文档核实）：
#   1. 一个服务只能监听一个端口；不支持 Docker Compose、不支持部署有状态服务（数据库等）；
#   2. 仅支持通过域名以 HTTP/HTTPS 调用；小程序端经 callContainer 调用无需配置合法域名。
#
# 基础镜像说明：requirements.txt 中 bcrypt 5.0.0 已核实发布 cp38-abi3
# manylinux wheel（bcrypt-5.0.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl），
# 故选用 slim 镜像无需编译工具链。若未来依赖变更导致个别包无 wheel，
# 可将下方 pip install 改为先安装编译工具：
#   RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依赖清单单独拷贝：依赖不变时命中 Docker 层缓存，避免每次重建都重装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码（app 包，含 main.py、api、core、db、models、schemas、services）
COPY app ./app

# 非 root 用户运行，降低容器逃逸风险
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# 硬编码监听 8080：非特权端口（>=1024），appuser 有权绑定；/health 为健康检查端点
ENV PORT=8080
EXPOSE 8080

# exec 格式直接启动 uvicorn（不经 sh -c），容器停止时进程直接收到 SIGTERM 优雅退出
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
