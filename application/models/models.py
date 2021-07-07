from application import app, db
from flask_login import (LoginManager,UserMixin,login_user,login_required,
logout_user,current_user)
from datetime import datetime

class User(db.Model,UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), nullable=False)
	email = db.Column(db.String(15), nullable=False)
	password = db.Column(db.String(80))
	user_image = db.Column(db.Text,nullable=False)
	post = db.relationship('Post',backref='user',lazy='dynamic')
	comment = db.relationship('Comments',backref='user',lazy='dynamic')
	followed = db.relationship('Follows',backref='user.followed_id',foreign_keys="Follows.followed_id",lazy='dynamic')
	followed_by = db.relationship('Follows',backref='user.followed_by_id',foreign_keys="Follows.followed_by_id",lazy='dynamic')
	to_be_notified = db.relationship('Notifications',backref='user.to_be_notified_id',foreign_keys="Notifications.to_be_notified_id",lazy='dynamic')
	action_by = db.relationship('Notifications',backref='user.action_by_id',foreign_keys="Notifications.action_by_id",lazy='dynamic')
	sender = db.relationship('Messages',backref='user.sender_id',foreign_keys="Messages.sender_id",lazy='dynamic')
	recepient = db.relationship('Messages',backref='user.recepient_id',foreign_keys="Messages.recepient_id",lazy='dynamic')


class Post(db.Model):
	post_id = db.Column(db.Integer, primary_key=True)
	post_body = db.Column(db.String(250), nullable=False)
	post_image = db.Column(db.Text,nullable=False)
	post_date = db.Column(db.DateTime(timezone=True), nullable=False)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	like = db.relationship('Likes',backref='post',lazy='dynamic')

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_body = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('post.post_id'))


class Likes(db.Model):
	like_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer,db.ForeignKey('post.post_id'))

class Follows(db.Model):
	follow_id = db.Column(db.Integer, primary_key=True)
	followed_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	followed_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class Notifications(db.Model):
	notification_id = db.Column(db.Integer, primary_key=True)
	to_be_notified_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	action_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer,db.ForeignKey('post.post_id'))
	is_like = db.Column(db.Integer,default=0)
	is_comment = db.Column(db.Integer,default=0)
	is_follow = db.Column(db.Integer,default=0)

class Messages(db.Model):
	message_id = db.Column(db.Integer, primary_key=True)
	message_body = db.Column(db.String(250), nullable=False)
	sender_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	recepient_id = db.Column(db.Integer,db.ForeignKey('user.id'))