from tests.conftest import EXAMPLE_URL


def test_create_page(client, auth_headers):
    response = client.get("/c", headers=auth_headers)
    assert response.status_code == 200


def test_create_url(client, auth_headers):
    response = client.post("/c", headers=auth_headers, data={
        "url": EXAMPLE_URL
    })
    assert response.status_code == 302


def test_dashboard_page(app, client, url_obj, auth_headers):
    response = client.get(f"/d/{url_obj.uuid}", headers=auth_headers)

    assert response.status_code == 200


def test_dashboard_edit(app, client, url_obj, auth_headers):
    response = client.post(f"/d/{url_obj.uuid}", headers=auth_headers, data={
        "url_to": EXAMPLE_URL,
        "path": "test",
        "use_js": False
    })

    assert response.status_code == 200


def test_redirector(app, client, url_obj):
    response = client.get(f"/{url_obj.path}")
    assert response.status_code == 302
    assert response.location == EXAMPLE_URL
