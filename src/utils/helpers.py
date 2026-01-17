import requests

def is_online():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False