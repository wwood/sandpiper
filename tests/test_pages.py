import pytest
import requests

PAGES = [
    "/",
    "/search",
    "/taxonomy/test",
    "/run/test",
    "/project",
    "/otus/test",
    "/random_run",
    "/accession/test",
    "/about",
]


@pytest.mark.parametrize("path", PAGES)
@pytest.mark.usefixtures("backend_server")
def test_frontend_pages(frontend_server, path):
    url = frontend_server + path
    response = requests.get(url)
    assert response.status_code == 200
