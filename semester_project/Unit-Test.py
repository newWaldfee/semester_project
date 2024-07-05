from medi_administration import app, users
from dicts import medications
import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'randomnumbersandletters'
    with app.test_client() as client:
        yield client


def test_register(client):
    user_data = {
        'name': 'Test',
        'email': 'test@test.com',
        'password': 'testpassword',
        'hospital_key': 'secret_hospital_key'
    }
    response = client.post('/register', data=user_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully registered! You can now login.' in response.data
    assert 'test@test.com' in users


def test_login(client):
    users['test@test.com'] = {
        'name': 'Test',
        'password': generate_password_hash('testpassword', method='pbkdf2:sha256')
    }
    login_data = {
        'email': 'test@test.com',
        'password': 'testpassword'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in as Test' in response.data


def test_medication_info(client):
    medications['TestMedi'] = {'dosage': '10mg', 'stock': 10, 'manufacturer': 'TestManufacturer'}
    info = {'name': 'TestMedi'}
    response = client.post('/info', data=info, follow_redirects=True)
    assert response.status_code == 200
    assert b'TestMedi' in response.data
    assert b'10mg' in response.data
    assert b'10' in response.data
    assert b'TestManufacturer' in response.data


def test_logout(client):
    users['test@mail.com'] = {
        'name': 'Test',
        'password': generate_password_hash('testpassword', method='pbkdf2:sha256')
    }
    login_data = {
        'email': 'test@mail.com',
        'password': 'testpassword'
    }
    client.post('/login', data=login_data, follow_redirects=True)

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Logout' not in response.data

