import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(): return TestClient(create_app())

def test_fixture_metrics_contract(client):
    response = client.get('/api/metrics')
    assert response.status_code == 200
    assert response.json()['revenue_cents'] == 685000
    assert response.json()['orders'] == 6
    assert response.json()['units'] == 10

def test_inclusive_filter(client):
    data = client.get('/api/metrics?start=2026-02-04&end=2026-02-18').json()
    assert data['revenue_cents'] == 305000
    assert data['orders'] == 2

@pytest.mark.parametrize('query,code',[('start=bad',422),('start=2026-05-01&end=2026-01-01',400)])
def test_rejected_filter(client,query,code):
    assert client.get('/api/metrics?'+query).status_code == code
    assert client.get('/api/metrics').json()['orders'] == 6

def test_empty_filter_is_success(client):
    result=client.get('/api/metrics?start=2027-01-01')
    assert result.status_code == 200
    assert result.json()['revenue_cents'] == 0

def test_missing_route(client):
    assert client.get('/api/not-found').status_code == 404
