from flask_blog import db, app
from author.form import RegisterForm, LoginForm
from flask import render_template, redirect, url_for, session, request, flash
from author.models import Author
from author.decorators import login_required
import bcrypt

@app.route('/login', methods=['GET','POST'])
def login():
	error=''
	form = LoginForm()
	if request.method=='GET' and request.args.get('next'):
			session['next'] = request.args.get('next',None)
	if form.validate_on_submit():
		author= Author.query.filter_by(username=form.username.data).first()
		if author:
			a=form.password.data
			b=author.password
			c=a.encode('utf8')
			d=b.encode('utf8')
			#if bcrypt.hashpw(form.password.data,author.password)==author.password:
			if bcrypt.hashpw(c,d)==d:
				session['username']=form.username.data
				session['is_author']=author.is_author
				session['id']=author.id
				flash('User %s is loggedin' %(form.username.data))
				if 'next' in session:
					next=session.get('next')
					session.pop('next')
					return redirect(next)
				else:	
					return redirect(url_for('index'))
			else:
				error='Incorrect username and password'
		else:
			error='Incorrect username and password'
	return render_template('author/login.html', form=form, error=error)
	
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        password = form.password.data
        hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
        author = Author(
            form.fullname.data,
            form.email.data,
            form.username.data,
            hashed_password,
            False
        )
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('author/register.html', form=form)
	
@app.route('/success')
def success():
	return "Author Registered!"
	
@app.route('/login_success')
@login_required
def login_success():
	return "Author login success!"
	
@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('is_author')
	session.pop('id')
	flash('User logged out')
	return redirect(url_for('login'))
	
