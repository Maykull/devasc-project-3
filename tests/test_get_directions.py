from app import app

def test_get_directions_valid():
    tester = app.test_client()
    response = tester.post('/get_directions', data={
        'start_loc': 'SM City Fairview',
        'dest_loc': 'SM City San Jose Del Monte',
        'vehicle': 'car'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "directions" in data
    assert "steps" in data
    assert "geometry" in data

def test_get_directions_invalid_location():
    tester = app.test_client()
    response = tester.post('/get_directions', data={
        'start_loc': 'NonexistentPlace',
        'dest_loc': 'AnotherNonexistentPlace',
        'vehicle': 'car'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
