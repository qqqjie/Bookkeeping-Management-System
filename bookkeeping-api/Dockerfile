# 个人记账管理系统 - 微信云托管部署镜像
#
# 构建上下文：bookkeeping-api/ 目录（与 requirements.txt、app/ 同级）
# 微信云托管规范（官方文档核实）：
#   1. 容器必须监听 PORT 环境变量指定的端口（默认 80），平台将外部 80/443 映射到该端口；
#   2. 一个服务只能监听一个端口；不支持 Docker Compose、不支持部署有状态服务（数据库等）；
#   3. 仅支持通过域名以 HTTP/HTTPS 调用。
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

# 云托管注入的 PORT 环境变量（默认 80）；/health 为健康检查端点
ENV PORT=80
EXPOSE 80

# exec 形式启动，确保容器停止时 uvicorn 能收到 SIGTERM 优雅退出
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-80}"]
