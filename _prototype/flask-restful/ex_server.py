
from flask import Flask, json, request
from flask_restful import Api, Resource
import jwt

app = Flask(__name__)
api = Api(app)

secret_key = 'secret'

def http_met(self):
    ticket = request.headers['ticket']
    print (ticket)
    print (jwt.decode(ticket, secret_key, algorithm='HS256')['user'])
    print (dir(request))
    print (request.base_url)
    print (request.host)
    print (request.host_url)
    print (request.url)
    print (request.path)
    print (request.url_root)
    print (request.url_rule)
    print (request.method)
    json_data = request.get_json(force=True)
    un = json_data["user"]
    pw = json_data["pass"]
    return app.response_class(
        response=json.dumps([{"u":un, "p":pw}]),
        status=200,
        #status=405,
        mimetype='application/json'
    )

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