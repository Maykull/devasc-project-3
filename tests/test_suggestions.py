from app import app

def test_suggestions_valid_query():
    tester = app.test_client()
    response = tester.get('/suggestions?query=University of Santo Tomas')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_suggestions_empty_query():
    tester = app.test_client()
    response = tester.get('/suggestions?query=')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []