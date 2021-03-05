#!/usr/bin/env python3

# Corona-Info-App
# Nutzerdatenbank
# © 2020 Tobias Höpp.

# Include dependencies
from main import db

# Class definition
class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.Text)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class tokens(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    def __init__(self, jti, token_type, user_identity, expires, revoked=False):
        self.jti = jti
        self.token_type = token_type
        self.user_identity = user_identity
        self.expires = expires
        self.revoked = revoked
    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }
    