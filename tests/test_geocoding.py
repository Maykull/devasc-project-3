from app import geocoding

def test_geocoding_valid_location():
    lat, lng, name = geocoding("Berlin", "fe27fd23-2c23-4019-a2b3-e316d862a3a1")
    assert lat is not None
    assert lng is not None
    assert name == "Berlin"

def test_geocoding_invalid_location():
    lat, lng, name = geocoding("NonexistentPlace", "fe27fd23-2c23-4019-a2b3-e316d862a3a1")
    assert lat is None
    assert lng is None
