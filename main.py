import os
from flask import Flask, abort, redirect, render_template, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SECRET_KEY'] = 'this is a secret'

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model Definitions
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
    comment = db.relationship('Comment', backref=db.backref('votes', lazy=True))



@app.route('/')
def index():
    try:
        popular_posts = Post.query\
            .join(Vote)\
            .filter(Vote.value == 1)\
            .group_by(Post)\
            .order_by(desc(func.count(Vote.id)))\
            .limit(6)\
            .all()
         
        recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    except:
        abort(500)

    return render_template('index.html', popular_posts=popular_posts, recent_posts=recent_posts)

from forms import LoginForm, SignUpForm, CreatePostForm

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).filter_by(password=form.password.data).first()

        if user is not None:
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)

        flash("Invalid username or password.")        
        
    return render_template('login.html', form=form, s="hello world")

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Sign up successful. You can now login.")
            return redirect(url_for('login'))
        except:
            abort(500)

        
    return render_template('signup.html', form=form)

from forms import CreateCategoryForm

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CreateCategoryForm()

    if form.validate_on_submit():
        try:
            new_category = Category(name=form.name.data)
            db.session.add(new_category)
            db.session.commit()

        except Exception as e:
            print(e)

        return redirect(url_for('categories', category_id=new_category.id))
    try:
        popular_categories = Category.query.join(Post)\
                                        .group_by(Category.id)\
                                        .order_by(db.func.count(Post.id).desc())\
                                        .limit(3).all()
        
        categories = Category.query.all()

    except Exception as e:
        abort(500)

    return render_template('categories.html', categories=categories, popular_categories=popular_categories, form=form)
    

@app.route('/categories/<category_id>', methods=["GET"])
@login_required
def category(category_id):
    try:
        category = Category.query.get(int(category_id))
        posts = Post.query.filter_by(category_id=category_id)\
                        .order_by(Post.created_at.desc()).all()
        return render_template('category.html', posts=posts, category=category)
    except Exception as e:
        print(e)
        abort(500)

from forms import CreateCommentForm

@app.route('/posts/<post_id>', methods=["GET", "POST"])
@login_required
def post(post_id):

    comment_form = CreateCommentForm()

    if comment_form.validate_on_submit():
        try:
            new_comment = Comment(
                content = comment_form.content.data,
                post_id = post_id,
                user_id = current_user.id
            )
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            print(e)

        return redirect(url_for('post', post_id=post_id))


    try:
        post = Post.query.get(int(post_id))
        upvote_count = Vote.query.filter_by(post=post, value=1).count()
        downvote_count = Vote.query.filter_by(post=post, value=-1).count()

        vote = Vote.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        upvoted = False
        downvoted = False

        if vote:
            if vote.value == 1:
                upvoted=True

            if vote.value == -1:
                downvoted = True

            


    except Exception as e:
        print(e)
        abort(500)

    return render_template('post.html', 
        post=post, 
        upvote_count=upvote_count, 
        downvote_count=downvote_count, 
        upvoted=upvoted, downvoted=downvoted,
        comment_form = comment_form
    )


@app.route('/posts/<post_id>/comments/<comment_id>/delete', methods=["POST"])
def delete_comment(post_id, comment_id):

    comment = Comment.query.filter_by(id=int(comment_id), post_id=post_id).first()

    if not post or not (comment.user_id == current_user.id):
        flash('Error deleting comment')
        return redirect(url_for('post', post_id=post_id)), 400
    
    try:
        db.session.delete(comment)
        db.session.commit()

    except Exception as e:
        print(e)
        return redirect(url_for('post', post_id=post_id)), 500

    finally:
        return redirect(url_for('post', post_id=post_id))


@app.route('/posts/<post_id>/upvote', methods=["POST"])
@login_required
def upvote(post_id):
    user_id = current_user.id

    try:
        vote = Vote.query.filter_by(post_id=int(post_id), user_id=int(user_id)).first()
        if vote:
            if vote.value != 1: # already voted
                vote.value = 1
                db.session.add(vote)
                db.session.commit()

            else:
                vote.value = 0
                db.session.add(vote)
                db.session.commit()

        else: # has not voted yet
            new_vote = Vote(post_id=int(post_id), user_id=int(user_id), value=1)
            db.session.add(new_vote)
            db.session.commit()

    except Exception as e:
        print(e)
        abort(500)

    return redirect(url_for('post', post_id=post_id))


@app.route('/posts/<post_id>/downvote', methods=["POST"])
@login_required
def downvote(post_id):
    user_id = current_user.id
    try:
        vote = Vote.query.filter_by(post_id=int(post_id), user_id=int(user_id)).first()
        if vote:
            if vote.value != -1: # already voted
                vote.value = -1
                db.session.add(vote)
                db.session.commit()

            else:
                vote.value = 0
                db.session.add(vote)
                db.session.commit()

        else: # has not voted yet
            new_vote = Vote(post_id=int(post_id), user_id=int(user_id), value=-1)
            db.session.add(new_vote)
            db.session.commit()

    except Exception as e:
        print(e)
        abort(500)

    return redirect(url_for('post', post_id=post_id))

from forms import SearchForm

@app.route('/posts', methods=["GET", "POST"])
@login_required
def posts():

    search_form = SearchForm()


    category_id = request.args.get('category_id')
    
    hot_categories = Category.query\
                .outerjoin(Category.posts)\
                .with_entities(Category, func.count(Post.id).label('post_count'))\
                .group_by(Category)\
                .order_by(desc('post_count'))\
                .limit(5)\
                .all()
    
    if search_form.validate_on_submit():
        print('hey')
        posts = Post.query.filter(Post.title.contains(search_form.text.data) | Post.content.contains(search_form.text.data)).all()
        return render_template('posts.html', posts=posts, hot_categories=hot_categories, search_form=search_form)
    

    if category_id:
        posts = Post.query.filter_by(category_id=category_id).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.filter_by(category_id=hot_categories[0][0].id).order_by(Post.created_at.desc()).all()
        
    return render_template('posts.html', posts=posts, hot_categories=hot_categories, search_form=search_form)

@app.route('/posts/create', methods=["GET", "POST"])
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        try:
            new_post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id,
                category_id=form.category.data
            )
        
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('post', post_id=new_post.id))

        except Exception as e:
            print(e)
            abort(500)

            

    return render_template('post_create.html', form=form)

from forms import EditPostForm

@app.route('/posts/<post_id>/edit', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    

    form = EditPostForm()
    post = Post.query.get(int(post_id))

    if not post or not (post.user_id == current_user.id):
        return redirect(url_for('index')) #TODO: add route for error pages


    if form.validate_on_submit():
        try:
            post.title = form.title.data
            post.content = form.content.data
            post.category_id = form.category.data
            print(post)
            db.session.add(post)
            db.session.commit()
            flash('Edit Successful.')
        except Exception as e:
            print('hey', e)
            flash('An error occured.')
        
        finally:
            return redirect(url_for('post', post_id=post_id))


    form.title.data = post.title
    form.content.data = post.content
    form.category.data = post.category_id

    return render_template('post_edit.html', form=form)


@app.route('/posts/<post_id>/delete', methods=["GET", "POST"])
def delete_post(post_id):

    post = Post.query.get(int(post_id))

    if not post or not (post.user_id == current_user.id):
        return redirect(url_for('post', post_id=post_id))
    
    if post:
        try:
            db.session.delete(post)
            db.session.commit()
            flash('Delete Successful')
        except Exception as e:
            print(e)
            flash('An error occured')

        finally:
            return redirect(url_for('user', user_id=current_user.id))




@app.route('/users/<user_id>')
@login_required
def user(user_id):
    
    user = User.query.get(user_id)
    if not user:
        abort(404)

    posts = Post.query.filter_by(user_id=user_id).all()

    return render_template('user.html', user=user, posts=posts)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)