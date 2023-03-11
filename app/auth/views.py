from . import auth
from .forms import LoginForm, SignUpForm
from flask_login import login_user, logout_user, login_required
from flask import render_template, url_for, redirect, request, flash, abort
from ..models import User
from .. import db

@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).filter_by(password=form.password.data).first()

        if user is not None:
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)

        flash("Invalid username or password.")        
        
    return render_template('login.html', form=form, s="hello world")



@auth.route('/signup', methods=["GET", "POST"])
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
            return redirect(url_for('.login'))
        except:
            abort(500)

        
    return render_template('signup.html', form=form)



@auth.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('.login'))