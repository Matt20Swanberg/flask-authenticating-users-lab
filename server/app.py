#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    """
    Handles user authentication through the /login endpoint

    Allows an existing user to log in using their username
    and stores their user ID in the Flask session
    """
    def post(self):
        """
        Authenticate a user using the provided username

        Returns:
            200: Serialized user data if authentication succeeds
            401: Error message if the username is not found
        """

        # Retrieve the user whose username matches the JSON request
        user = User.query.filter(User.username == request.get_json()['username']).first()

        if user:
            # Store the authenticated user's ID in the session
            session['user_id'] = user.id

            # Serialize and return the authenticated user's data
            return UserSchema().dump(user), 200
        
        else:
            # Reject the login attempt if no matching user exists
            return {'message': 'Invalid Login'}, 401

class CheckSession(Resource):
    """
    Handles session verification through /check_session.

    Determines whether the current session belongs to a
    valid user and returns their information if authenticated
    """

    def get(self):
        """
        Retrieve the currently authenticated user

        Returns:
            200: Serialized user data if the session is valid
            401: Empty response data if no valid user is found
        """

        # Look up the user associated with the stored session ID
        # session.get() returns None if user_id does not exist
        user = User.query.filter(
            User.id == session.get('user_id')
        ).first()

        if user:
            # Return the authenticated user's serialized data
            return UserSchema().dump(user), 200

        else:
            # Deny access when the session has no valid user
            return {}, 401

class Logout(Resource):
    """
    Handles user logout through the /logout endpoint

    Removes the authenticated user's ID from the Flask session,
    ending their current login session
    """

    def delete(self):
        """
        Log out the current user by clearing their session ID

        Returns:
            204: Successful logout with no response content
        """

        # Remove user_id without raising an error if it is absent
        session.pop('user_id', None)

        # Return HTTP 204 to indicate a successful logout
        return {'message': '204: No Content'}, 204

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
