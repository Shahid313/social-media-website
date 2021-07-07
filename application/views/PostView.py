from flask_classful import FlaskView, route
from application.models.models import *
from flask import render_template, request
from application import db
from flask import redirect, url_for
from application.forms.forms import *
from application.utils import save_file
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from application import login_manager
from sqlalchemy import text
import json

class PostView(FlaskView):
	@route('/',methods=['GET','POST'])
	@login_required 
	def post(self):
		if request.method == 'POST':
			if current_user.is_authenticated:
				curr_user = current_user
				post_body = request.form.get("body")
				post_image = request.files['post-image']
				isSaved, file_name = save_file(post_image,'post_images')
				new_post = Post(post_body=post_body,post_date = datetime.now(),
					            user_id=curr_user.id,post_image=file_name)
			try:
				db.session.add(new_post)
				db.session.commit()
				return redirect(url_for('PostView:post'))
			except Exception as e:
				return "There was an issue in posting"+str(e)
		else:
			if current_user.is_authenticated:
				curr_user = current_user
			sql = text("(SELECT post.*, user.* FROM follows RIGHT JOIN post on post.user_id = follows.followed_id LEFT JOIN user on user.id = post.user_id WHERE follows.followed_by_id = "+str(curr_user.id)+") UNION (SELECT post.*, user.* FROM post LEFT JOIN user on user.id = post.user_id WHERE post.user_id = "+str(curr_user.id)+") ORDER BY post_date DESC") 
			posts = db.engine.execute(sql)
			posts_res = list()
			for post in posts:
				data = dict()
				comment_sql = text("SELECT * FROM comments LEFT JOIN user on user.id = comments.author_id WHERE post_id = "+str(post.post_id))
				post_comments = db.engine.execute(comment_sql)

				data['post_comments'] = post_comments
				data["post_data"] = post

				posts_res.append(data)

			if current_user.is_authenticated:
				curr_user = current_user
				users = User.query.filter_by(id=curr_user.id)
				user_sql = text("SELECT * FROM user WHERE id != "+str(curr_user.id))
				f_users = db.engine.execute(user_sql)

			sql = text("SELECT * FROM notifications LEFT JOIN user on user.id = notifications.action_by_id WHERE to_be_notified_id = "+str(curr_user.id))
			notifications = db.engine.execute(sql)
			return render_template('home.html',posts_res=posts_res,users=users,f_users=f_users,notifications=notifications)


	@route('/comment/<int:id>',methods=['GET','POST'])
	def comment(self,id):
		posts = Post.query.get_or_404(id)
		if current_user.is_authenticated:
			curr_user = current_user
		if request.method == 'POST':
			comment_body = request.form.get('comment-body')
			new_comment = Comments(comment_body=comment_body,post_id=posts.post_id,author_id=curr_user.id)
			db.session.add(new_comment)
			db.session.commit()
			comment_notification = Notifications(to_be_notified_id=posts.user_id,action_by_id=curr_user.id,is_comment=1)
			db.session.add(comment_notification)
			db.session.commit()
			return redirect(url_for('PostView:post'))
		else:
			return render_template('home.html',posts=posts)

	@route('/likes/<int:id>')
	def likes(self,id):
		posts = Post.query.get_or_404(id)
		if current_user.is_authenticated:
		 	curr_user = current_user

		like = Likes.query.filter_by(user_id=curr_user.id, post_id=posts.post_id)
		if like.count() > 0:
			db.session.delete(like.first())
			db.session.commit()
		notification_to_delete = Notifications.query.filter_by(post_id=posts.post_id,action_by_id=curr_user.id,is_like=1)
		if notification_to_delete.count() > 0:
			db.session.delete(notification_to_delete.first())
			db.session.commit()
			return redirect(url_for('PostView:post'))
		else:
			new_like = Likes(post_id=posts.post_id,user_id=curr_user.id)
			try:
				db.session.add(new_like)
				db.session.commit()
				like_notification = Notifications(to_be_notified_id=posts.user_id,
					                               action_by_id=curr_user.id,post_id=posts.post_id,is_like=1)
				db.session.add(like_notification)
				db.session.commit()
				return redirect(url_for('PostView:post'))
			except Exception as e:
				return "There was an issue in liking the post"+str(e)
		return render_template('home.html')

	@route('/follows/<int:id>')
	def follows(self,id):
		users = User.query.get_or_404(id)
		if current_user.is_authenticated:
			curr_user = current_user

		follow = Follows.query.filter_by(followed_id=users.id,followed_by_id=curr_user.id)
		if follow.count() > 0:
			db.session.delete(follow.first())
			db.session.commit()
		follow_to_delete = Notifications.query.filter_by(to_be_notified_id=users.id,action_by_id=curr_user.id,is_follow=1)
		if follow_to_delete.count() > 0:
			db.session.delete(follow_to_delete.first())
			db.session.commit()
			return redirect(url_for('PostView:post'))
		else:
			new_follow = Follows(followed_id=users.id,followed_by_id=curr_user.id)
			try:
				db.session.add(new_follow)
				db.session.commit()
				follow_notification = Notifications(to_be_notified_id=users.id,action_by_id=curr_user.id,is_follow=1)
				db.session.add(follow_notification)
				db.session.commit()
				return redirect(url_for('PostView:post'))
			except Exception as e:
				return "There was an issue in following this man "+str(e)

	@route('/messages')
	def messages(self):
		if current_user.is_authenticated:
			curr_user = current_user
		people_sql = text("SELECT * FROM user WHERE id != "+str(curr_user.id))
		people = db.engine.execute(people_sql)
		return render_template('messages.html', people=people)

	@route('/send_message/<int:id>',methods=['GET','POST'])
	def send_message(self,id):
		users = User.query.get_or_404(id)
		user_id = users.id
		if request.method == 'POST':
			if current_user.is_authenticated:
				curr_user = current_user
			message_body = request.form.get("message-body")
			new_message = Messages(message_body=message_body,recepient_id=user_id,sender_id=curr_user.id)
			try:
				db.session.add(new_message)
				db.session.commit()
				return redirect(url_for('PostView:send_message',id=id))
			except Exception as e:
				return "There was an issue in sending message "+str(e)
		else:
			if current_user.is_authenticated:
				curr_user = current_user
			message_sql = text("SELECT *, IF(sender_user.id="+str(curr_user.id)+", true, false) as amISender "
				+"FROM messages LEFT JOIN user as sender_user on sender_user.id = messages.sender_id "
				+"LEFT JOIN user as rec_user on rec_user.id = messages.recepient_id "
				+"WHERE (sender_id = "+str(curr_user.id)+" AND recepient_id = "+str(user_id)+") "+
				"OR (sender_id = "+str(user_id)+" AND recepient_id = "+str(curr_user.id)+")")
			messages = db.engine.execute(message_sql)
			return render_template('send_message.html',messages=messages,users=users)




			




