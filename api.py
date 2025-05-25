import requests

def fetch_posts():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()