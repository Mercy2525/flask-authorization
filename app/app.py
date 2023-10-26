#!/usr/bin/env python3
import os
from flask import Flask, make_response, jsonify, request,session
from flask_migrate import Migrate
from models import db, User
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt=Bcrypt(app)
# development
app.secret_key='Benjie$'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR']= True
migrate = Migrate(app, db,render_as_batch=True)

db.init_app(app)
api = Api(app)
CORS(app)



class Index(Resource):
    def get(self):
        response_body = '<h1>Hello World</h1>'
        status = 200
        headers = {}
        return make_response(response_body,status,headers)
    

class Signup(Resource):
    def post(self):
        name=request.get_json().get('name')
        password=request.get_json().get('name')

        if name and password:
            new_user=User(name=name)
            new_user.password_hash=password

            db.session.add(new_user)
            db.session.commit()

            #create a cookie using session,name it as user_id
            session['user_id']=new_user.id

            return new_user.to_dict(), 201
        
        return {"error": "user details must be added"},401
    

api.add_resource(Signup,'/signup', endpoint='signup')

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user=user.query.filter(user.id==session['user_id'])
            return user.to_dict(), 200
        
        return {"error": "Resource not found"}
api.add_resource(CheckSession, '/checksession', endpoint='/checksession')

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id']=None
            return {"success": " you have been logged out successfully"}
        else:
            return {"error": "you have no account, login(create a session)"}

class Login(Resource):
    def post(self):
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter(User.name==name).first()
        if user and user.authenticate(password):
            session['user_id']=user.id
            return user.to_dict(),200
        else:
            return {'error':'username or password incorrect'},

api.add_resource(Login, '/login', endpoint = 'login')
        

class Users(Resource):
    def get(self):
        users = []
        for user in User.query.all():
            user_dict={
                "name":user.name,
            }
            users.append(user_dict)
        response= make_response(
                jsonify(users),
                200
                )
        return response
    
    def post(self):
        new_user = User(
            name=request.form.get("name"),
        )

        db.session.add(new_user)
        db.session.commit()

        user_dict = new_user.to_dict()

        response = make_response(
            jsonify(user_dict),
            201
        )

        return response



class UserById(Resource):
    def get(self,id):
        user = User.query.filter_by(id=id).first()
        user_dict = user.to_dict()
        response = make_response(
        jsonify(user_dict),
        200
        )
        response.headers["Content-Type"]= "application/json"
        return response
        
    def patch(self,id):
        user = User.query.filter_by(id=id).first()

        for attr in request.form:
            setattr(user, attr, request.form.get(attr))

        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()

        response = make_response(
            jsonify(user_dict),
            200
        )

        return response

    def delete(self,id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()

        response_dict = {
            "delete_successful": True,
            "message": "User deleted."    
        }

        response = make_response(
            jsonify(response_dict),
            200
        )

        return response




@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found:The requested resource does not exist",
        404
        )
    return response

api.add_resource(Index,'/', endpoint='landing')
api.add_resource(Users, '/users', endpoint='user')
api.add_resource(UserById,'/users/<int:id>', endpoint ='user_id')

if __name__ == '__main__':
    app.run(port=5000)