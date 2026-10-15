"""前后端联调全流程：针对已运行的服务（前端 5173 / 后端 8080）执行。

覆盖前端会走通的完整链路：访问页面 → 注册 → 登录 → 建账户 → 记账 →
查余额/列表/统计 → 退出登录（前端侧清令牌）→ 清理测试数据。
不启动任何子进程，全部请求打向正在运行的服务。

运行：python scripts/e2e_running.py
"""

import json
import sys
import time
import urllib.error
import urllib.request

FRONTEND = "http://127.0.0.1:5173"
BACKEND = "http://127.0.0.1:8080/api/v1"

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


def call(method, path, body=None, token=None, base=BACKEND):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(base + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


print("== 0. 前端页面可访问 ==")
try:
    with urllib.request.urlopen(FRONTEND + "/", timeout=10) as response:
        html = response.read().decode("utf-8", errors="replace")
    check("前端首页返回 200", response.status == 200)
    check("页面挂载点存在", 'id="app"' in html, html[:120])
except Exception as exc:  # noqa: BLE001
    check("前端首页可访问", False, str(exc))

print("== 1. 注册 ==")
suffix = str(int(time.time()))
username = f"e2e_{suffix}"
status, body = call(
    "POST",
    "/auth/register",
    {
        "username": username,
        "email": f"{username}@example.com",
        "password": "abc12345",
        "nickname": "联调用户"
    },
)
check("注册成功（信封结构 code/message/data）", status == 200 and body.get("code") == 200, body)
check("返回 token 与用户信息", "token" in body["data"] and "user" in body["data"], body)
check("用户信息不含密码字段", "passwordHash" not in body["data"]["user"], body)
token = body["data"]["token"]

print("== 2. 登录 ==")
status, body = call("POST", "/auth/login", {"loginId": username, "password": "abc12345"})
check("登录成功", status == 200 and body.get("code") == 200, body)
token = body["data"]["token"]

print("== 3. 当前用户 ==")
status, body = call("GET", "/users/me", token=token)
check("获取当前用户", body["data"]["username"] == username, body)

print("== 4. 建账户 ==")
status, body = call(
    "POST",
    "/accounts",
    {"accountName": "联调储蓄卡", "accountType": "debit_card", "initialBalance": "3000.00"},
    token,
)
check("创建账户", status == 200 and body["data"]["initialBalance"] == "3000.00", body)
check("金额为字符串类型", isinstance(body["data"]["initialBalance"], str), body)
account_id = body["data"]["accountId"]

print("== 5. 记账（支出 + 收入）==")
status, body = call("GET", "/categories", token=token)
food = next(c for c in body["data"] if c["categoryName"] == "餐饮")
salary = next(c for c in body["data"] if c["categoryName"] == "工资")

status, expense = call(
    "POST",
    "/transactions",
    {
        "accountId": account_id,
        "categoryId": food["categoryId"],
        "transactionType": "expense",
        "amount": "88.80",
        "transactionTime": "2026-10-15T12:30:00",
        "remark": "联调晚餐"
    },
    token,
)
check("记一笔支出", status == 200 and expense["data"]["amount"] == "88.80", expense)
status, income = call(
    "POST",
    "/transactions",
    {
        "accountId": account_id,
        "categoryId": salary["categoryId"],
        "transactionType": "income",
        "amount": "6000.00",
        "transactionTime": "2026-10-15T18:00:00"
    },
    token,
)
check("记一笔收入", status == 200, income)

print("== 6. 查余额与列表 ==")
status, body = call("GET", f"/accounts/{account_id}/balance", token=token)
check("余额 = 3000 - 88.80 + 6000", body["data"] == "8911.20", body)
status, body = call("GET", "/accounts", token=token)
balances = {item["accountId"]: item["currentBalance"] for item in body["data"]}
check("账户列表含实时余额", balances.get(account_id) == "8911.20", body)

status, body = call("GET", "/transactions?page=1&size=10", token=token)
page = body["data"]
check("流水列表分页字段", page["total"] == 2 and len(page["records"]) == 2, body)
check("按交易时间倒序", page["records"][0]["amount"] == "6000.00", body)
check("流水金额为字符串", isinstance(page["records"][0]["amount"], str), body)

print("== 7. 图表数据 ==")
status, body = call("GET", "/stats/monthly-summary", token=token)
check("月度汇总", body["data"]["totalIncome"] == "6000.00" and body["data"]["totalExpense"] == "88.80", body)
status, body = call("GET", "/stats/category-share?transactionType=expense", token=token)
check("分类占比", body["data"][0]["categoryName"] == "餐饮" and body["data"][0]["percentage"] == "100.00", body)
status, body = call("GET", "/stats/trend?months=6", token=token)
check("趋势 6 个月", len(body["data"]) == 6, body)

print("== 8. 退出登录（前端侧行为模拟）==")
# 退出登录 = 前端清除 token；模拟清除后访问受保护接口应 401
status, body = call("GET", "/users/me")
check("清除令牌后访问受保护接口返回 401", status == 401 and body["code"] == 401, body)
# 原令牌此时在后端仍然有效（无状态 JWT），属于预期行为
status, body = call("GET", "/users/me", token=token)
check("服务端无状态，旧令牌在过期前仍有效（预期）", status == 200, body)

print("== 9. 清理测试数据 ==")
status, _ = call("DELETE", f"/transactions/{expense['data']['transactionId']}", token=token)
status2, _ = call("DELETE", f"/transactions/{income['data']['transactionId']}", token=token)
status3, _ = call("DELETE", f"/accounts/{account_id}", token=token)
check("清理流水与账户", status == 200 and status2 == 200 and status3 == 200, f"{status}/{status2}/{status3}")

print(f"\n结果: {passed} 通过, {failed} 失败")
sys.exit(1 if failed else 0)
