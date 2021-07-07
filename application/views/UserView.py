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

@login_manager.user_loader 
def load_user(user_id):
	return User.query.get(int(user_id))

class UserView(FlaskView):
	@route('/login',methods=['GET','POST'])
	def login(self):
		form = LoginForm()
		if form.validate_on_submit():
			user = User.query.filter_by(username=form.username.data).first()
			if user:
				if check_password_hash(user.password,form.password.data):
					login_user(user)
					return redirect(url_for('PostView:post'))
				else:
					return "Your password is incorrect"
			else:
				return "This user does not exist"
		else:
			return render_template('login.html',form=form)

	@route('/signup',methods=['GET','POST'])
	def signup(self):
		form = SignupForm()
		if form.validate_on_submit():
			hashed_password = generate_password_hash(form.password.data,method='sha256')
			isSaved, file_name = save_file(form.user_image.data,'user_images')
			if isSaved:
				new_user = User(username=form.username.data,email=form.email.data,
					            password=hashed_password,user_image=file_name)
			try:
				db.session.add(new_user)
				db.session.commit()
				return redirect(url_for('UserView:login'))
			except:
				return "There was an issue"

		return render_template('signup.html',form=form)

	@route("/logout")
	@login_required
	def logout(self):
		logout_user()
		return redirect(url_for('UserView:login'))

	@route('/profile',methods=['GET','POST'])
	def profile(self):
		form = UpdateSignupForm()
		if current_user.is_authenticated:
			curr_user = current_user
		post_sql = text("SELECT * FROM post WHERE user_id = "+str(curr_user.id))
		user_posts = db.engine.execute(post_sql)
		if form.validate_on_submit():
			if request.method == 'POST':
				if current_user.is_authenticated:
					curr_user = current_user
				curr_user.username = form.username.data
				curr_user.email = form.email.data
				isSaved,file_name = save_file(form.user_image.data,'user_images')
				curr_user.user_image = file_name
				hashed_password = generate_password_hash(form.password.data,method='sha256')
				curr_user.password = hashed_password
				try:
					db.session.commit()
					return redirect(url_for('PostView:post'))
				except Exception as e:
					return "There was an issue in updating"+str(e)
			else:
				return render_template('profile.html',form=form)
		else:
			return render_template('profile.html',form=form,user_posts=user_posts)


