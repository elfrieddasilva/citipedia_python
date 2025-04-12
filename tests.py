import requests

BASE_URL = "http://127.0.0.1:5000/best_path"


def test_best_path():
    params = {
        "dest_lat": 6.3912755,
        "dest_lnhg": 2.3859534027275098,
        "transportation": "bike"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        print("Response JSON:", response.json())
    else:
        print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    test_best_path()
