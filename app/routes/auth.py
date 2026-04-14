from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Topic, TopicProgress
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_seen = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}! 🎯', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        # Init progress for all topics
        topics = Topic.query.all()
        for topic in topics:
            progress = TopicProgress(user_id=user.id, topic_id=topic.id)
            db.session.add(progress)
        db.session.commit()
        login_user(user)
        flash('Account created! Start your UGC NET journey. 🚀', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'danger')
            else:
                current_user.email = email
                flash('Email updated.', 'success')
        if new_password:
            if new_password != confirm:
                flash('Passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                current_user.set_password(new_password)
                flash('Password updated.', 'success')
        db.session.commit()
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html')
