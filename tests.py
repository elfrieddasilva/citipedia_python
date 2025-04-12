import requests

BASE_URL = "http://127.0.0.1:5000/best_path"


def test_best_path():
    params = {
        "origin_lat": 6.36793655,
        "origin_lng": 2.4776425249858725,
        "dest_lat": 6.3912755,
        "dest_lng": 2.3859534027275098
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        print("Response JSON:", response.json())
    else:
        print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    test_best_path()
