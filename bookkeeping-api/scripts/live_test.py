"""真实 MySQL 连接测试：数据库直连 + 启动 FastAPI + 走通 README 第九节全流程。

前置条件：
  1. MySQL 已就绪且 3306 可连（Docker 容器 bookkeeping-mysql，或等价实例）；
  2. db/schema.sql 已执行（Docker 首次启动会自动执行 init/01-schema.sql）；
  3. bookkeeping_app 账户已创建并授权（D:\bookkeeping-mysql\app_user.sql）；
  4. 项目根目录 .env 已配置 MYSQL_USER / MYSQL_PASSWORD。

运行：PYTHONPATH=. python scripts/live_test.py
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pymysql

from app.core.config import get_settings

BASE = "http://127.0.0.1:8080/api/v1"

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -> {detail}")


def http(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def check_database(settings):
    """以 .env 中的 bookkeeping_app 账户直连数据库。"""
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        charset="utf8mb4",
        connect_timeout=10,
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.execute("SHOW TABLES")
        tables = sorted(row[0] for row in cursor.fetchall())
    connection.close()
    print(f"  数据库版本: {version}，用户: {settings.mysql_user}")
    check("数据库连接成功（MySQL 8.x）", version.startswith("8."), version)
    check(
        "四张表齐全",
        tables == ["accounts", "categories", "transactions", "users"],
        tables,
    )


def wait_for_server(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=3):
                return True
        except Exception:  # noqa: BLE001
            time.sleep(1)
    return False


def run_api_flow():
    suffix = str(int(time.time()))
    username = f"live_{suffix}"

    print("== 1. 注册 ==")
    status, body = http(
        "POST",
        "/auth/register",
        {
            "username": username,
            "email": f"{username}@example.com",
            "password": "abc12345",
            "nickname": "联调测试",
        },
    )
    check("注册成功", status == 200 and body.get("code") == 200, body)
    token = body["data"]["token"]

    print("== 2. 登录 ==")
    status, body = http(
        "POST", "/auth/login", {"loginId": username, "password": "abc12345"}
    )
    check("登录成功", status == 200 and body.get("code") == 200, body)
    token = body["data"]["token"]

    print("== 3. 建账户 ==")
    status, body = http(
        "POST",
        "/accounts",
        {
            "accountName": "联调工资卡",
            "accountType": "debit_card",
            "initialBalance": "2000.00",
        },
        token,
    )
    check("创建账户", status == 200 and body.get("code") == 200, body)
    account_id = body["data"]["accountId"]

    print("== 4. 分类与记账 ==")
    status, body = http("GET", "/categories", token=token)
    categories = body["data"]
    food = next(c for c in categories if c["categoryName"] == "餐饮")
    salary = next(c for c in categories if c["categoryName"] == "工资")
    check(
        "系统预设分类可见（餐饮/工资）",
        food is not None and salary is not None,
        categories,
    )

    status, body = http(
        "POST",
        "/transactions",
        {
            "accountId": account_id,
            "categoryId": food["categoryId"],
            "transactionType": "expense",
            "amount": "35.50",
            "transactionTime": "2026-10-15T12:00:00",
            "remark": "联调午饭",
        },
        token,
    )
    check("记一笔支出", status == 200 and body.get("code") == 200, body)
    expense_id = body["data"]["transactionId"]

    status, body = http(
        "POST",
        "/transactions",
        {
            "accountId": account_id,
            "categoryId": salary["categoryId"],
            "transactionType": "income",
            "amount": "5000.00",
            "transactionTime": "2026-10-15T18:00:00",
        },
        token,
    )
    check("记一笔收入", status == 200 and body.get("code") == 200, body)
    income_id = body["data"]["transactionId"]

    print("== 5. 查余额 ==")
    status, body = http("GET", f"/accounts/{account_id}/balance", token=token)
    check("余额 = 2000 - 35.50 + 5000", body["data"] == "6964.50", body)

    status, body = http("GET", "/accounts", token=token)
    balances = {item["accountId"]: item["currentBalance"] for item in body["data"]}
    check("账户列表含实时余额", balances.get(account_id) == "6964.50", body)

    print("== 6. 统计 ==")
    status, body = http("GET", "/stats/monthly-summary", token=token)
    check("月度收入 5000.00", body["data"]["totalIncome"] == "5000.00", body)
    check("月度支出 35.50", body["data"]["totalExpense"] == "35.50", body)
    check("月度净额 4964.50", body["data"]["netAmount"] == "4964.50", body)

    status, body = http(
        "GET", "/stats/category-share?transactionType=expense", token=token
    )
    check("分类占比金额 35.50", body["data"][0]["amount"] == "35.50", body)
    check("分类占比 100.00%", body["data"][0]["percentage"] == "100.00", body)

    status, body = http("GET", "/stats/trend?months=6", token=token)
    check("趋势返回 6 个月", len(body["data"]) == 6, body)

    print("== 7. 清理测试数据 ==")
    status, _ = http("DELETE", f"/transactions/{expense_id}", token=token)
    status2, _ = http("DELETE", f"/transactions/{income_id}", token=token)
    status3, _ = http("DELETE", f"/accounts/{account_id}", token=token)
    check(
        "清理流水与账户",
        status == 200 and status2 == 200 and status3 == 200,
        f"{status}/{status2}/{status3}",
    )


def main():
    settings = get_settings()
    print("== 0. 数据库直连检查 ==")
    try:
        check_database(settings)
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] 数据库连接失败 -> {exc}")
        print("\n结果: 0 通过, 1 失败")
        print("提示：MySQL 未就绪。请先完成 Docker 部署（D:\\bookkeeping-mysql）")
        print("      或在 .env 中指向一个已就绪的 MySQL 实例。")
        sys.exit(1)

    env = dict(os.environ)
    env["PYTHONPATH"] = os.getcwd()
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
    )
    try:
        if not wait_for_server():
            print("  [FAIL] FastAPI 服务启动超时")
            sys.exit(1)
        print("  FastAPI 服务已启动（http://127.0.0.1:8080）")
        run_api_flow()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    print(f"\n结果: {passed} 通过, {failed} 失败")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
