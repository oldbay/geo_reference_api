
import json
import requests
import jwt

user = 'myuser'
secret_key = 'secret'
ticket = jwt.encode({'user': 'myuser'}, secret_key, algorithm='HS256')


url = 'http://127.0.0.1:5444/hello'
headers = {
    'Content-Type': 'application/json', 
    'ticket': ticket,
}

data = {"pass": "my pass", "user": "my user"}
response = requests.get(url, data=json.dumps(data), headers=headers)
print(response.status_code)
print(response.json())
