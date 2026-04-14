from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import Subject, Topic, ExamSession, Question

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    paper1_subjects = Subject.query.filter_by(paper='paper1').order_by(Subject.order).all()
    paper2_subjects = Subject.query.filter_by(paper='paper2').order_by(Subject.order).all()
    total_topics = Topic.query.count()
    total_questions = Question.query.count()
    stats = {
        'total_topics': total_topics,
        'total_questions': total_questions,
        'paper1_subjects': len(paper1_subjects),
        'paper2_subjects': len(paper2_subjects),
    }
    return render_template('index.html',
                           paper1_subjects=paper1_subjects,
                           paper2_subjects=paper2_subjects,
                           stats=stats)

@main_bp.route('/about')
def about():
    return render_template('about.html')
