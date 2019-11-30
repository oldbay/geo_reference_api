
import json
import requests
import jwt

user = 'myuser'
secret_key = 'secret'
ticket = jwt.encode({'user': 'myuser'}, secret_key, algorithm='HS256')


urls = [
    'http://127.0.0.1:5444/hello1', 
    'http://127.0.0.1:5444/hello2',
]
for url in urls:
    headers = {
        'Content-Type': 'application/json', 
        'ticket': ticket,
    }
    
    data = {"pass": "my pass", "user": "my user"}
    response = requests.get(url, data=json.dumps(data), headers=headers)
    print (url)
    print ('GET')
    print(response.status_code)
    print(response.json())
    
    data = {"pass": "my pass", "user": "my user"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print (url)
    print ('POST')
    print(response.status_code)
    print(response.json())
    
    data = {"pass": "my pass", "user": "my user"}
    response = requests.put(url, data=json.dumps(data), headers=headers)
    print (url)
    print ('PUT')
    print(response.status_code)
    print(response.json())
    
    data = {"pass": "my pass", "user": "my user"}
    response = requests.delete(url, data=json.dumps(data), headers=headers)
    print (url)
    print ('DELETE')
    print(response.status_code)
    print(response.json())
