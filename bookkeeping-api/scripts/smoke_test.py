"""端到端冒烟测试：SQLite 内存库 + TestClient，不依赖 MySQL。

覆盖：注册/登录、账户 CRUD 与实时余额、分类合并与二级分类、
交易筛选/分页/倒序、三个统计接口、越权隔离、删除保护。
运行：python scripts/smoke_test.py
"""

import sys
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models import Category
from app.models.enums import CategoryType

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)
Base.metadata.create_all(engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

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


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def register(username, email, password="abc12345"):
    return client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password, "nickname": username},
    )


# 模拟 db/schema.sql 中的系统预设分类种子数据
db = TestingSessionLocal()
for name, icon, order in [("餐饮", "food", 1), ("交通", "transport", 2), ("工资", "salary", 10)]:
    db.add(
        Category(
            user_id=None,
            category_name=name,
            category_type=CategoryType.EXPENSE if name != "工资" else CategoryType.INCOME,
            icon=icon,
            sort_order=order,
            status=1,
        )
    )
db.commit()
db.close()

print("== 1. 注册与登录 ==")
r = register("yuqie", "yuqie@example.com")
check("注册成功并返回 token", r.status_code == 200 and r.json()["data"]["token"], r.text)
token_a = r.json()["data"]["token"]
user_a = r.json()["data"]["user"]
check("响应为 camelCase 信封", set(r.json()) >= {"code", "message", "data"}, r.text)
check("用户 VO 不含密码字段", "passwordHash" not in user_a, r.text)

r = register("yuqie", "another@example.com")
check("重复用户名 409", r.status_code == 409, r.text)

r = register("weakpwd", "weak@example.com", password="1234567")
check("弱密码 400", r.status_code == 400, r.text)

r = client.post("/api/v1/auth/login", json={"loginId": "yuqie", "password": "wrong-pass"})
check("错误密码 401", r.status_code == 401, r.text)

r = client.post("/api/v1/auth/login", json={"loginId": "yuqie@example.com", "password": "abc12345"})
check("邮箱亦可登录", r.status_code == 200, r.text)
token_a = r.json()["data"]["token"]

r = client.get("/api/v1/users/me")
check("无 token 401", r.status_code == 401, r.text)
r = client.get("/api/v1/users/me", headers=headers(token_a))
check("获取当前用户", r.json()["data"]["username"] == "yuqie", r.text)

print("== 2. 账户与实时余额 ==")
r = client.post(
    "/api/v1/accounts",
    json={"accountName": "招行信用卡", "accountType": "credit_card", "initialBalance": "1000.00"},
    headers=headers(token_a),
)
check("创建账户", r.status_code == 200, r.text)
card_id = r.json()["data"]["accountId"]
check("金额以字符串返回", r.json()["data"]["initialBalance"] == "1000.00", r.text)

r = client.post(
    "/api/v1/accounts",
    json={"accountName": "招行信用卡", "accountType": "credit_card"},
    headers=headers(token_a),
)
check("重名账户 409", r.status_code == 409, r.text)

r = client.post(
    "/api/v1/accounts",
    json={"accountName": "现金", "accountType": "cash", "initialBalance": "500.00"},
    headers=headers(token_a),
)
cash_id = r.json()["data"]["accountId"]

print("== 3. 分类：系统+自定义合并、二级分类 ==")
r = client.get("/api/v1/categories", headers=headers(token_a))
cats = r.json()["data"]
check("系统分类可见且排序", [c["categoryName"] for c in cats] == ["餐饮", "交通", "工资"], r.text)

r = client.post(
    "/api/v1/categories",
    json={"categoryName": "餐饮", "categoryType": "expense"},
    headers=headers(token_a),
)
check("同名同类型分类 409", r.status_code == 409, r.text)

r = client.post(
    "/api/v1/categories",
    json={"categoryName": "下午茶", "categoryType": "expense", "parentId": cats[0]["categoryId"]},
    headers=headers(token_a),
)
check("二级分类创建", r.status_code == 200, r.text)
child_id = r.json()["data"]["categoryId"]

print("== 4. 交易：筛选/分页/倒序 ==")
food_id = cats[0]["categoryId"]
salary_id = cats[2]["categoryId"]
now = datetime.now()
noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
morning = noon - timedelta(hours=2)
last_month_dt = now.replace(day=1) - timedelta(days=5)
this_month = now.strftime("%Y-%m")
last_month = last_month_dt.strftime("%Y-%m")

client.post(
    "/api/v1/transactions",
    json={
        "accountId": card_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "35.50", "transactionTime": morning.isoformat(), "remark": "午饭",
    },
    headers=headers(token_a),
)
client.post(
    "/api/v1/transactions",
    json={
        "accountId": cash_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "20.00", "transactionTime": (noon - timedelta(hours=1)).isoformat(),
    },
    headers=headers(token_a),
)
client.post(
    "/api/v1/transactions",
    json={
        "accountId": card_id, "categoryId": salary_id, "transactionType": "income",
        "amount": "8000.00", "transactionTime": noon.isoformat(),
    },
    headers=headers(token_a),
)
client.post(
    "/api/v1/transactions",
    json={
        "accountId": card_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "99.99", "transactionTime": last_month_dt.isoformat(),
    },
    headers=headers(token_a),
)

r = client.get("/api/v1/transactions?page=1&size=2", headers=headers(token_a))
page = r.json()["data"]
check("分页总数", page["total"] == 4, r.text)
check("倒序排列", page["records"][0]["amount"] == "8000.00", r.text)
check("分页字段", page["pages"] == 2 and page["page"] == 1 and page["size"] == 2, r.text)

r = client.get(f"/api/v1/transactions?month={this_month}", headers=headers(token_a))
check("按月份筛选", r.json()["data"]["total"] == 3, r.text)
r = client.get(f"/api/v1/transactions?month={last_month}", headers=headers(token_a))
check("按上月筛选", r.json()["data"]["total"] == 1, r.text)
r = client.get("/api/v1/transactions?transactionType=income", headers=headers(token_a))
check("按类型筛选", r.json()["data"]["total"] == 1, r.text)
r = client.get(f"/api/v1/transactions?accountId={card_id}", headers=headers(token_a))
check("按账户筛选", r.json()["data"]["total"] == 3, r.text)
r = client.get("/api/v1/transactions?size=0", headers=headers(token_a))
check("分页参数校验 400", r.status_code == 400, r.text)
r = client.post(
    "/api/v1/transactions",
    json={
        "accountId": card_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "-5.00", "transactionTime": noon.isoformat(),
    },
    headers=headers(token_a),
)
check("负数金额 400", r.status_code == 400, r.text)

print("== 5. 实时余额 ==")
r = client.get(f"/api/v1/accounts/{card_id}/balance", headers=headers(token_a))
check("信用卡余额 = 1000 + 8000 - 35.50 - 99.99", r.json()["data"] == "8864.51", r.text)
r = client.get("/api/v1/accounts", headers=headers(token_a))
balances = {a["accountId"]: a["currentBalance"] for a in r.json()["data"]}
check("列表含实时余额", balances[card_id] == "8864.51", r.text)
check("现金余额 = 500 - 20", balances[cash_id] == "480.00", r.text)

print("== 6. 统计接口 ==")
r = client.get(f"/api/v1/stats/monthly-summary?month={this_month}", headers=headers(token_a))
data = r.json()["data"]
check("月度收入", data["totalIncome"] == "8000.00", r.text)
check("月度支出", data["totalExpense"] == "55.50", r.text)
check("月度净额", data["netAmount"] == "7944.50", r.text)
check("月度笔数", data["incomeCount"] == 1 and data["expenseCount"] == 2, r.text)

r = client.get(f"/api/v1/stats/category-share?month={this_month}", headers=headers(token_a))
share = r.json()["data"]
check("分类占比金额", share[0]["amount"] == "55.50", r.text)
check("分类占比百分比", share[0]["percentage"] == "100.00", r.text)

r = client.get("/api/v1/stats/trend?months=6", headers=headers(token_a))
trend = r.json()["data"]
check("趋势返回 6 个月", len(trend) == 6, r.text)
check("趋势按月份正序", trend[0]["month"] < trend[-1]["month"], r.text)
current_item = [t for t in trend if t["month"] == this_month][0]
check("趋势本月支出", current_item["totalExpense"] == "55.50", r.text)
check("趋势本月收入", current_item["totalIncome"] == "8000.00", r.text)
last_item = [t for t in trend if t["month"] == last_month][0]
check("趋势上月支出", last_item["totalExpense"] == "99.99", r.text)

print("== 7. 越权隔离 ==")
r = register("intruder", "intruder@example.com")
token_b = r.json()["data"]["token"]
r = client.get(f"/api/v1/accounts/{card_id}", headers=headers(token_b))
check("他人账户 404", r.status_code == 404, r.text)
r = client.get("/api/v1/transactions", headers=headers(token_b))
check("他人流水不可见", r.json()["data"]["total"] == 0, r.text)
r = client.post(
    "/api/v1/transactions",
    json={
        "accountId": card_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "1.00", "transactionTime": noon.isoformat(),
    },
    headers=headers(token_b),
)
check("他人账户不可记账 404", r.status_code == 404, r.text)
r = client.get("/api/v1/categories", headers=headers(token_b))
check("系统分类对所有用户可见", len(r.json()["data"]) == 3, r.text)
r = client.delete(f"/api/v1/categories/{food_id}", headers=headers(token_b))
check("系统分类不可删 404", r.status_code == 404, r.text)

print("== 8. 删除保护 ==")
r = client.delete(f"/api/v1/accounts/{card_id}", headers=headers(token_a))
check("有流水账户删除 409", r.status_code == 409, r.text)
txs = client.get("/api/v1/transactions?size=100", headers=headers(token_a)).json()["data"]["records"]
for tx in txs:
    client.delete(f"/api/v1/transactions/{tx['transactionId']}", headers=headers(token_a))
r = client.delete(f"/api/v1/accounts/{card_id}", headers=headers(token_a))
check("清空流水后可删除账户", r.status_code == 200, r.text)
r = client.delete(f"/api/v1/categories/{child_id}", headers=headers(token_a))
check("子分类可删除", r.status_code == 200, r.text)

print("== 9. 更新 ==")
r = client.put("/api/v1/users/me", json={"nickname": "玉切"}, headers=headers(token_a))
check("更新昵称", r.json()["data"]["nickname"] == "玉切", r.text)
r = client.put(
    f"/api/v1/accounts/{cash_id}",
    json={"accountName": "现金钱包", "accountType": "cash", "initialBalance": "600.00"},
    headers=headers(token_a),
)
check("更新账户", r.json()["data"]["accountName"] == "现金钱包", r.text)
tx_id = client.post(
    "/api/v1/transactions",
    json={
        "accountId": cash_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "12.00", "transactionTime": noon.isoformat(),
    },
    headers=headers(token_a),
).json()["data"]["transactionId"]
r = client.put(
    f"/api/v1/transactions/{tx_id}",
    json={
        "accountId": cash_id, "categoryId": food_id, "transactionType": "expense",
        "amount": "15.00", "transactionTime": noon.isoformat(),
    },
    headers=headers(token_a),
)
check("更新流水", r.json()["data"]["amount"] == "15.00", r.text)

print(f"\n结果: {passed} 通过, {failed} 失败")
sys.exit(1 if failed else 0)
