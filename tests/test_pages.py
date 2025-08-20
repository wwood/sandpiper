import os
import signal
import subprocess
import time
import requests
from html.parser import HTMLParser

BACKEND_URL = "http://localhost:6000"
FRONTEND_URL = "http://localhost:6173"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = None
        for attr, value in attrs:
            if attr == "href":
                href = value
                break
        if href:
            self.links.add(href)


def wait_for(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Timeout waiting for {url}")


import pytest

@pytest.fixture(scope="session", autouse=True)
def servers():
    env = os.environ.copy()
    env["SANDPIPER_TESTING"] = "1"

    backend_cmd = [
        "pixi",
        "run",
        "-e",
        "sandpiper",
        "flask",
        "--app",
        "wsgi.py",
        "run",
        "-p",
        "6000",
        "--no-reload",
    ]
    backend = subprocess.Popen(
        backend_cmd, cwd="backend", env=env, start_new_session=True
    )

    frontend_cmd = [
        "pixi",
        "run",
        "-e",
        "sandpiper",
        "npm",
        "run",
        "dev",
        "--",
        "--port",
        "6173",
    ]
    frontend = subprocess.Popen(
        frontend_cmd, cwd="vue", env=env, start_new_session=True
    )

    try:
        wait_for(f"{BACKEND_URL}/api/sandpiper_stats")
        wait_for(FRONTEND_URL)
        yield
    finally:
        for proc in (frontend, backend):
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        for proc in (frontend, backend):
            try:
                proc.wait(timeout=10)
            except Exception:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


def test_pages():
    session = requests.Session()
    pages = {
        "/",
        "/search",
        "/taxonomy/Bacteria",
        "/run/ERR2194039",
        "/project",
        "/otus/ERR2194039",
        "/random_run",
        "/accession/ERR2194039",
        "/about",
    }

    resp = session.get(FRONTEND_URL + "/run/ERR2194039")
    assert resp.status_code == 200
    parser = LinkParser()
    parser.feed(resp.text)

    api_links = set()
    for href in parser.links:
        if href.startswith("http://localhost:6000"):
            api_links.add(href)
        elif href.startswith("http://localhost:6173"):
            pages.add(href[len("http://localhost:6173"):])
        elif href.startswith("/"):
            pages.add(href)

    for path in pages:
        r = session.get(FRONTEND_URL + path)
        assert r.status_code == 200, f"{path} returned {r.status_code}"

    for url in api_links:
        r = session.get(url)
        assert r.status_code == 200, f"{url} returned {r.status_code}"
