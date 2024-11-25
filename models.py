# models.py

from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_image = db.Column(db.String(150), default='/api/placeholder/...')
    is_admin = db.Column(db.Boolean, default=False)

    # Relacionamento many-to-many entre usuários e grupos
    groups = db.relationship('Group', secondary='group_members', back_populates='members')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.String(300))
    categories = db.Column(db.String(150))  # Campo para categorias
    member_count = db.Column(db.Integer, default=0)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    online_members = db.Column(db.Integer, default=0)

    # Relacionamento many-to-many entre usuários e grupos
    members = db.relationship('User', secondary='group_members', back_populates='groups')
    admin = db.relationship('User', backref=db.backref('admin_groups', lazy=True))

# Tabela de associação para relacionamento many-to-many
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('group_messages', lazy=True))
    group = db.relationship('Group', backref=db.backref('messages', lazy=True))

class ContactForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
