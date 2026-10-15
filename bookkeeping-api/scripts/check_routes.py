"""打印全部已注册路由，用于核对 API 清单。运行：PYTHONPATH=. python scripts/check_routes.py"""

from app.main import app

paths = sorted(
    (method, path)
    for route in app.routes
    for method in getattr(route, "methods", set()) or set()
    if (path := getattr(route, "path", None))
)
print(f"共 {len(paths)} 个端点：")
for method, path in paths:
    print(f"  {method:6s} {path}")
