#!/usr/bin/env python3


# Login API endpoint
from main import api, jwt, db
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_raw_jwt, decode_token, set_access_cookies, unset_jwt_cookies
from models.users import users, tokens
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime

# SEE: https://github.com/vimalloc/flask-jwt-extended/tree/master/examples/database_blacklist

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@api.route('/edit/auth/login', methods=['POST'])
def login():
    if request.json:
        inputs = request.json
    else:
        inputs = request.form.to_dict()
    username = inputs.get('username', None)
    password = inputs.get('password', None)
    if not username:
        return jsonify({"status":"RequiredValueError","value":"username"}), 400
    if not password:
        return jsonify({"status":"RequiredValueError","value":"username"}), 400
    
    # Check Credentials
    try:
        u = users.query.filter(users.username == inputs.get("username"), users.password == inputs.get("password")).one()
    except MultipleResultsFound:
        return jsonify({"status":"InternalServerError", "error":"Multiple users found. This should not have happend."}), 500
    except NoResultFound:
        return jsonify({"status": "CredentialsError", "msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=u.username)
    # Store the tokens in our store with a status of not currently revoked.
    decoded_token = decode_token(access_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token[api.config['JWT_IDENTITY_CLAIM']]
    expires = datetime.fromtimestamp(decoded_token['exp'])

    db_token = tokens(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=False,
    )
    db.session.add(db_token)
    db.session.commit()
    resp = jsonify({"access_token":access_token})
    # TODO:give a choice wether you want a cookie or a token
    set_access_cookies(resp, access_token)
    return resp, 201

# Endpoint for revoking the current users access token
@api.route('/edit/auth/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    token = tokens.query.filter_by(jti=jti).one()
    token.revoked = True
    db.session.commit()
    resp = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(resp)
    return resp, 200

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@api.route('/edit/auth/currentUser', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    print(decoded_token)
    jti = decoded_token['jti']
    try:
        token = tokens.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"status":"ExpiredAccessToken", "error":"The token is no longer valid"}), 401

@jwt.revoked_token_loader
@jwt.invalid_token_loader
def revoked_token_callback(arg=None):
    return jsonify({"status":"InvalidAccessToken", "error":"The token is not valid"}), 401