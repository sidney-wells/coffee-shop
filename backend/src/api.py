import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


db_drop_and_create_all()


@app.route('/drinks', methods=['GET'])
def get_drinks(*args, **kwargs):
    
    drinks = Drink.query.order_by(Drink.id).all()
    
    drinks = [drink.short() for drink in drinks]
    
    if len(drinks) == 0:
        drinks = []

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(*args, **kwargs):
    
    drinks = Drink.query.order_by(Drink.id).all()
        
    drinks = [drink.long() for drink in drinks]
        
    if len(drinks) == 0:
        drinks = []
    
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(*args, **kwargs):
    
    body = request.get_json()
    
    if body is None:
        abort(404)
    
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    
    try:
        drink = Drink(title=title, recipe=json.dumps([recipe]))
        drink.insert()
        
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except():
        abort(404)
    
    
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(*args, **kwargs):
    
    drink_id = kwargs['drink_id']
    
    body = request.get_json()
    
    if body is None:
        abort(404)
        
    title = body.get('title', None)
    recipe = body.get('recipe', None)
        
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    try:
        drink.title = title
        
        drink.recipe = json.dumps([recipe])
         
        drink.update()
      
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except():
        abort(404)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):

    drink_id = kwargs['drink_id']

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    })


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        'error': 422,
        'message': "unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'authorization failed'
    })


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        'error': 400,
        'message': "bad request"
    }), 400


@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        'error': 405,
        'message': "method not allowed"
    }), 405


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        'error': 404,
        'message': "resource not found"
    }), 404


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'forbidden'
    })


@app.errorhandler(AuthError)
def auth_failed(AuthError):
    res = jsonify(AuthError.error)
    res.status_code = AuthError.status_code
    return res
