"""启动 uvicorn 并探测 /health、/openapi.json、/docs，验证服务可真实启动。

运行：PYTHONPATH=. python scripts/check_server.py
"""

import json
import os
import subprocess
import sys
import time
import urllib.request

PORT = 8017
BASE = f"http://127.0.0.1:{PORT}"

env = dict(os.environ)
env["PYTHONPATH"] = os.getcwd()

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=env,
    text=True,
)

try:
    time.sleep(5)
    for path in ("/health", "/openapi.json", "/docs"):
        try:
            with urllib.request.urlopen(BASE + path, timeout=5) as response:
                body = response.read().decode("utf-8", errors="replace")
                print(f"{path}: HTTP {response.status}, {len(body)} bytes")
                if path == "/openapi.json":
                    paths = [key for key in json.loads(body)["paths"] if key.startswith("/api/")]
                    print(f"  /api/v1 端点共 {len(paths)} 个：")
                    for item in sorted(paths):
                        print(f"    {item}")
        except Exception as exc:  # noqa: BLE001
            print(f"{path}: 失败 -> {exc}")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
