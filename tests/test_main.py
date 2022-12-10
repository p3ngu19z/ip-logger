from src.models import URL, db


def test_create_page(client, auth_headers):
    response = client.get("/c", headers=auth_headers)
    assert response.status_code == 200


def test_create_url(client, auth_headers):
    response = client.post("/c", headers=auth_headers, data={
        "url": "https://example.com/"
    })
    assert response.status_code == 302


def test_dashboard_page(app, client, auth_headers):
    with app.app_context():
        url_obj = URL(url_to="https://example.com")
        db.session.add(url_obj)
        db.session.commit()

        response = client.get(f"/d/{url_obj.uuid}", headers=auth_headers)

        assert response.status_code == 200

        db.session.delete(url_obj)
        db.session.commit()


def test_dashboard_edit(app, client, auth_headers):
    with app.app_context():
        url_obj = URL(url_to="https://example.com")
        db.session.add(url_obj)
        db.session.commit()

        response = client.post(f"/d/{url_obj.uuid}", headers=auth_headers, data={
            "url_to": "https://example.com",
            "name": "test",
            "use_js": False
        })

        assert response.status_code == 200

        db.session.delete(url_obj)
        db.session.commit()


def test_redirector(app, client):
    with app.app_context():
        url_obj = URL(url_to="https://example.com")
        db.session.add(url_obj)
        db.session.commit()

        response = client.get(f"/{url_obj.name}")

        assert response.status_code == 302
        assert response.location == "https://example.com"

        db.session.delete(url_obj)
        db.session.commit()
