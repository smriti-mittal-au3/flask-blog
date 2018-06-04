from flask_blog import app
from flask import render_template, redirect, url_for, session, abort, request
from blog.form import SetupForm, PostForm
from flask_blog import db, uploaded_images
from author.models import Author
from blog.models import Blog, Category, Post
from flask import flash
from author.decorators import login_required, author_required
import bcrypt
from slugify import slugify

POSTS_PER_PAGE=5

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
@login_required
def index(page=1):
	#blog=Blog.query.first()
	user_id = session.get('id')
	print(user_id)
	blog = Blog.query.filter_by(admin=user_id).first() #if user has created a blog, then, get it
	print(blog)
	if not blog:
		return redirect(url_for('setup'))
	posts=Post.query.filter_by(live=True, author_id=user_id).order_by(Post.publish_date.desc()).paginate(page,POSTS_PER_PAGE,True)
	return render_template('blog/index.html', blog=blog, posts=posts)
	
	
@app.route('/admin')
#@author_required
@login_required
def admin():

	user_id = session.get('id')
	print(user_id)
	blog = Blog.query.filter_by(admin=user_id).first()
	print(blog)
	#if session.get('is_author'):
	#if not Post.query.filter_by(author_id=user_id):
	#	return redirect(url_for('post'))
	posts=Post.query.filter_by(author_id=user_id).order_by(Post.publish_date.desc())
	return render_template('blog/admin.html', posts=posts)
	#else:
	#	return abort(403)
	
@app.route('/setup', methods=['GET','POST'])
def setup():
	form = SetupForm()
	error=""
	if form.validate_on_submit():
		salt = bcrypt.gensalt()
		pssword =form.password.data
		hashed_password = bcrypt.hashpw(pssword.encode('utf8'),salt)
		author = Author(form.fullname.data,
					form.email.data,
					form.username.data,
					hashed_password,
					True)
		db.session.add(author)
		db.session.flush()
		if author.id:
			blog = Blog(form.name.data, author.id)
			db.session.add(blog)
			db.session.flush()
			if blog.id:
				db.session.commit()
				flash("Blog Created")
				return redirect(url_for('admin'))
			else:
				db.session.rollback()
				error = "Blog not created"
		else:
			db.session.rollback()
			error ="Author not created"
			
	return render_template('blog/setup.html', form=form, error=error)

@app.route('/post',methods=['GET','POST'])
#@author_required
def post():
	form = PostForm()
	if form.validate_on_submit():
		image=request.files.get('image')
		filename=None
		try:
			filename=uploaded_images.save(image)
		except:
			flash("image not uploaded")
		if form.new_category.data:
			category=Category(form.new_category.data)
			db.session.add(category)
			db.session.flush()
		elif form.category.data:
			category_id=form.category.get_pk(form.category.data)
			category=Category.query.filter_by(id=category_id).first()
		else:
			category=None
		blog=Blog.query.first()
		author=Author.query.filter_by(username=session['username']).first()
		title=form.title.data
		body=form.body.data
		
		slug=slugify(title)
		post = Post(blog,author,category,title,body,filename,slug)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('article', slug=slug))
			
	return render_template('blog/post.html', form=form, action="new")
	
@app.route('/article/<slug>')
def article(slug):
	author=False
	post=Post.query.filter_by(slug=slug).first_or_404()
	if session.get('id')==post.author_id:
		author=True
	return render_template('blog/article.html', post=post, author=author)
	
@app.route('/delete/<int:post_id>')
#@author_required
def delete(post_id):
	post=Post.query.filter_by(id=post_id).first_or_404()
	post.live=False
	db.session.commit()
	flash("post deleted")
	return redirect('/admin')
	
@app.route('/edit/<int:post_id>', methods=['POST','GET'])
#@author_required
def edit(post_id):
	post=Post.query.filter_by(id=post_id).first_or_404()
	form=PostForm(obj=post)
	if form.validate_on_submit():
		original_image=post.image
		form.populate_obj(post)
		if form.new_category.data:
			new_category=Category(form.new_category.data)
			db.session.add(new_category)
			db.session.flush()
			post.category=new_category
		if form.image.has_file():	
			image=request.files.get('image')
			try:
				filename=uploaded_images.save(image)
				post.image=filename
			except:
				flash("new image file not uploaded")
		else:
			post.image=original_image
		db.session.commit()
		return redirect(url_for('article',slug=post.slug))
	return render_template('blog/post.html', form=form, post=post, action="edit")