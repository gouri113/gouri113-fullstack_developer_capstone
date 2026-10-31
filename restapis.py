import os
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")


def get_request(endpoint, **kwargs):
    """
    Make a GET request to the Node.js / Express backend service.
    """
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + str(value) + "&"

    request_url = backend_url.rstrip("/") + "/" + endpoint.lstrip("/")
    if params:
        request_url = request_url.rstrip("&")
        request_url = request_url + "?" + params

    print(f"GET from {request_url}")
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred while requesting {request_url}: {err}")
        return None
    except ValueError as err:
        print(f"Failed to parse JSON response from {request_url}: {err}")
        return None


def analyze_review_sentiments(text):
    """
    Make a GET request to the sentiment analyzer microservice.
    """
    base_url = sentiment_analyzer_url.rstrip("/")
    quoted_text = urllib.parse.quote(text)
    request_url = f"{base_url}/analyze/{quoted_text}"
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Sentiment analysis network exception for {request_url}: {err}")
        return None
    except ValueError as err:
        print(f"Failed to parse JSON sentiment response from {request_url}: {err}")
        return None


def post_review(data_dict):
    """
    Make a POST request to insert a review into the Express/MongoDB service.
    """
    request_url = backend_url.rstrip("/") + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred while posting review to {request_url}: {err}")
        return None
    except ValueError as err:
        print(f"Failed to parse JSON response from {request_url}: {err}")
        return None
