
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import jwt

app = Flask(__name__)
api = Api(app)

secret_key = 'secret'

class HelloWorld(Resource):

    def get(self):
        ticket = request.headers['ticket']
        print (ticket)
        print (jwt.decode(ticket, secret_key, algorithm='HS256')['user'])
        json_data = request.get_json(force=True)
        un = json_data["user"]
        pw = json_data["pass"]
        return jsonify(u=un, p=pw)
    

api.add_resource(HelloWorld, '/hello')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5444, debug=True)