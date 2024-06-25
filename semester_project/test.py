from medi_administration import medications, app
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'randomnumbersandletters'
    with app.test_client() as client:
        yield client


def test_add_medi(client):
    medi_to_add = {'name': 'TestName',
                   'dosage': 'xxmg',
                   'stock': '1',
                   'manufacturer': 'TestManufacturer'}
    start_count = len(medications)
    response = client.post('/add', data=medi_to_add, follow_redirects=True)
    assert response.status_code == 200
    assert len(medications) == start_count + 1
    assert b'TestName' in response.data


def test_update_stock(client):
    medications['TestMedi'] = {'dosage': '10mg', 'stock': 10, 'manufacturer': 'TestManufacturer'}
    update = {'name': 'TestMedi', 'taken': '5'}
    response = client.post('/update', data=update, follow_redirects=True)
    assert response.status_code == 200
    assert medications['TestMedi']['stock'] == 5


def test_restock(client):
    medications['TestMedi'] = {'dosage': '10mg', 'stock': 10, 'manufacturer': 'TestManufacturer'}
    restock = {'name': 'TestMedi', 'restock': '20'}
    response = client.post('/restock', data=restock, follow_redirects=True)
    assert response.status_code == 200
    assert medications['TestMedi']['stock'] == 30


def test_medication_info(client):
    medications['TestMedi'] = {'dosage': '10mg', 'stock': 10, 'manufacturer': 'TestManufacturer'}
    info = {'name': 'TestMedi'}
    response = client.post('/info', data=info, follow_redirects=True)
    assert response.status_code == 200
    assert b'TestMedi' in response.data
    assert b'10mg' in response.data
    assert b'10' in response.data
    assert b'TestManufacturer' in response.data
