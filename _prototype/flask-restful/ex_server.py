
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import copy
import jwt

app = Flask(__name__)
api = Api(app)

secret_key = 'secret'

def http_met(self):
    ticket = request.headers['ticket']
    print (ticket)
    print (jwt.decode(ticket, secret_key, algorithm='HS256')['user'])
    json_data = request.get_json(force=True)
    un = json_data["user"]
    pw = json_data["pass"]
    return jsonify(u=un, p=pw)

api_cont_dict = {
    "hello1": {
        "get": http_met,
        "put": http_met,
    },
    "hello2": {
        "post": http_met,
        "delete": http_met,
    },
}

for api_key in api_cont_dict:
    api.add_resource(
        type(api_key, (Resource,), api_cont_dict[api_key]),
        '/{}'.format(api_key)
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5444, debug=True)