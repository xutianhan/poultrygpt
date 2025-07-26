import requests

url = "http://175.27.253.234:8000/api/chat"
data = {
    "user_id": "user123",
    "session_id": "session456",
    "query": "鸡冠肿胀",
    "intent": "diagnose",
    "entities": ["鸡冠肿胀", "呼吸困难"]
}

response = requests.post(url, json=data)
print(response.json())