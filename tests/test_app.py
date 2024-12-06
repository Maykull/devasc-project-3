from app import app

def test_welcome():
    tester = app.test_client()
    response = tester.get('/')
    assert response.status_code == 200

def test_index():
    tester = app.test_client()
    response = tester.get('/index')
    assert response.status_code == 200

def test_travel_tips():
    tester = app.test_client()
    response = tester.get('/travel-tips')
    assert response.status_code == 200
