from services.thumbnail.service import extract_thumbnail_url


def test_thumbnail_extraction():
    data = {
        "itinerary": {
            "days": [
                {"day": 1, "thumbnail_url": "img1.jpg"}
            ]
        }
    }

    assert extract_thumbnail_url(data) == "img1.jpg"