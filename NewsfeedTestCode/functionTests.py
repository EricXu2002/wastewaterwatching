import pytest

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        with app.app.app_context():
            app.db.create_all()
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_about(client):
    response = client.get('/about')
    assert response.status_code == 200

def test_map(client):
    response = client.get('/map')
    assert response.status_code == 200

def test_news(client):
    response = client.get('/news')
    assert response.status_code == 200

def test_forum(client):
    response = client.get('/forum')
    assert response.status_code == 200

def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_signup(client):
    response = client.get('/signup')
    assert response.status_code == 200

def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 200