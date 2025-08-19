import os
import subprocess
import time
from pathlib import Path

import pytest
import requests

BACKEND_PORT = 5001
FRONTEND_PORT = 8080

def _wait_for_server(url: str, timeout: int = 120):
    """Wait until a server responds at the given URL."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"Server {url} did not start in time")


@pytest.fixture(scope="session")
def backend_server():
    env = os.environ.copy()
    env["SANDPIPER_TESTING"] = "1"
    env["FLASK_APP"] = "api.application:create_app"
    cmd = [
        "pixi",
        "shell",
        "-e",
        "sandpiper",
        "-c",
        f"flask run --port {BACKEND_PORT} --host 127.0.0.1",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=Path(__file__).resolve().parents[1] / "backend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_server(f"http://127.0.0.1:{BACKEND_PORT}")
        yield f"http://127.0.0.1:{BACKEND_PORT}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def frontend_server(backend_server):
    env = os.environ.copy()
    # ensure npm does not attempt to open browser
    env["BROWSER"] = "none"
    vue_dir = Path(__file__).resolve().parents[1] / "vue"
    if not (vue_dir / "node_modules").exists():
        pytest.fail("node_modules missing - run npm install")
    cmd = [
        "pixi",
        "shell",
        "-e",
        "sandpiper",
        "-c",
        f"npm run serve -- --port {FRONTEND_PORT}",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=vue_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_server(f"http://127.0.0.1:{FRONTEND_PORT}", timeout=240)
        yield f"http://127.0.0.1:{FRONTEND_PORT}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
