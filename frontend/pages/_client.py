import os

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get(path: str, **params):
    response = requests.get(f"{API_BASE_URL}{path}", params=params or None, timeout=30)
    response.raise_for_status()
    return response.json()


def post(path: str, json=None, files=None, data=None):
    response = requests.post(f"{API_BASE_URL}{path}", json=json, files=files, data=data, timeout=90)
    response.raise_for_status()
    return response.json()


def patch(path: str, json=None):
    response = requests.patch(f"{API_BASE_URL}{path}", json=json, timeout=30)
    response.raise_for_status()
    return response.json()
