from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Subject, Topic, TopicProgress, StudySession
import markdown
from datetime import datetime

topics_bp = Blueprint('topics', __name__)

def md_to_html(text):
    if not text:
        return ''
    return markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br'])

@topics_bp.route('/')
def index():
    paper = request.args.get('paper', 'all')
    if paper == 'paper1':
        subjects = Subject.query.filter_by(paper='paper1').order_by(Subject.order).all()
    elif paper == 'paper2':
        subjects = Subject.query.filter_by(paper='paper2').order_by(Subject.order).all()
    else:
        subjects = Subject.query.order_by(Subject.paper, Subject.order).all()

    user_progress = {}
    if current_user.is_authenticated:
        progress_records = TopicProgress.query.filter_by(user_id=current_user.id).all()
        user_progress = {p.topic_id: p for p in progress_records}

    return render_template('topics/index.html', subjects=subjects,
                           paper=paper, user_progress=user_progress)

@topics_bp.route('/<slug>')
def detail(slug):
    topic = Topic.query.filter_by(slug=slug).first_or_404()
    content_html = md_to_html(topic.content)

    progress = None
    if current_user.is_authenticated:
        progress = TopicProgress.query.filter_by(
            user_id=current_user.id, topic_id=topic.id).first()

    # Sibling topics for navigation
    siblings = Topic.query.filter_by(subject_id=topic.subject_id).order_by(Topic.order).all()
    idx = next((i for i, t in enumerate(siblings) if t.id == topic.id), 0)
    prev_topic = siblings[idx - 1] if idx > 0 else None
    next_topic = siblings[idx + 1] if idx < len(siblings) - 1 else None

    return render_template('topics/detail.html', topic=topic,
                           content_html=content_html, progress=progress,
                           prev_topic=prev_topic, next_topic=next_topic)

@topics_bp.route('/<slug>/complete', methods=['POST'])
@login_required
def mark_complete(slug):
    topic = Topic.query.filter_by(slug=slug).first_or_404()
    progress = TopicProgress.query.filter_by(
        user_id=current_user.id, topic_id=topic.id).first()
    if not progress:
        progress = TopicProgress(user_id=current_user.id, topic_id=topic.id)
        db.session.add(progress)

    minutes = int(request.form.get('minutes', 0))
    progress.completed = True
    progress.completed_at = datetime.utcnow()
    progress.last_studied = datetime.utcnow()
    progress.study_minutes += minutes

    # Log study session
    if minutes > 0:
        ss = StudySession(user_id=current_user.id, topic_id=topic.id,
                          duration_minutes=minutes)
        db.session.add(ss)
        current_user.total_study_minutes += minutes

    db.session.commit()
    flash(f'"{topic.title}" marked as complete! ✅', 'success')
    return redirect(url_for('topics.detail', slug=slug))

@topics_bp.route('/<slug>/notes', methods=['POST'])
@login_required
def save_notes(slug):
    topic = Topic.query.filter_by(slug=slug).first_or_404()
    progress = TopicProgress.query.filter_by(
        user_id=current_user.id, topic_id=topic.id).first()
    if not progress:
        progress = TopicProgress(user_id=current_user.id, topic_id=topic.id)
        db.session.add(progress)
    progress.notes = request.form.get('notes', '')
    db.session.commit()
    return jsonify({'status': 'ok'})

@topics_bp.route('/api/subjects')
def api_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'paper': s.paper} for s in subjects])
