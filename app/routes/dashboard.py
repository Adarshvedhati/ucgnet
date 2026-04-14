from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import TopicProgress, ExamSession, StudySession, Subject, Topic
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Overall progress
    total_topics = Topic.query.count()
    completed_topics = TopicProgress.query.filter_by(
        user_id=current_user.id, completed=True).count()
    progress_percent = round((completed_topics / total_topics * 100) if total_topics > 0 else 0)

    # Paper-wise progress
    paper1_topics = Topic.query.join(Subject).filter(Subject.paper == 'paper1').count()
    paper2_topics = Topic.query.join(Subject).filter(Subject.paper == 'paper2').count()

    paper1_done = db.session.query(TopicProgress).join(Topic).join(Subject)\
        .filter(TopicProgress.user_id == current_user.id,
                TopicProgress.completed == True,
                Subject.paper == 'paper1').count()
    paper2_done = db.session.query(TopicProgress).join(Topic).join(Subject)\
        .filter(TopicProgress.user_id == current_user.id,
                TopicProgress.completed == True,
                Subject.paper == 'paper2').count()

    # Exam stats
    exam_sessions = ExamSession.query.filter_by(
        user_id=current_user.id, completed=True).all()
    avg_score = round(sum(s.score_percent for s in exam_sessions) / len(exam_sessions), 1) \
        if exam_sessions else 0
    best_score = round(max((s.score_percent for s in exam_sessions), default=0), 1)

    # Recent exams
    recent_exams = ExamSession.query.filter_by(
        user_id=current_user.id, completed=True
    ).order_by(ExamSession.completed_at.desc()).limit(5).all()

    # Study time this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_study = db.session.query(func.sum(StudySession.duration_minutes))\
        .filter(StudySession.user_id == current_user.id,
                StudySession.created_at >= week_ago).scalar() or 0

    # Daily study data (last 14 days)
    daily_data = []
    for i in range(13, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        mins = db.session.query(func.sum(StudySession.duration_minutes))\
            .filter(StudySession.user_id == current_user.id,
                    StudySession.session_date == day).scalar() or 0
        daily_data.append({'date': day.strftime('%b %d'), 'minutes': mins})

    # Score trend
    score_trend = [{'date': s.completed_at.strftime('%b %d'),
                    'score': s.score_percent,
                    'title': s.title}
                   for s in reversed(exam_sessions[-10:])]

    # Subject progress
    subjects = Subject.query.order_by(Subject.paper, Subject.order).all()
    subject_progress = []
    for subj in subjects:
        s_total = subj.topics.count()
        s_done = db.session.query(TopicProgress)\
            .join(Topic).filter(Topic.subject_id == subj.id,
                                TopicProgress.user_id == current_user.id,
                                TopicProgress.completed == True).count()
        subject_progress.append({
            'name': subj.name,
            'paper': subj.paper,
            'icon': subj.icon,
            'color': subj.color,
            'total': s_total,
            'done': s_done,
            'percent': round((s_done / s_total * 100) if s_total > 0 else 0)
        })

    # Incomplete topics (to suggest)
    incomplete_progress = db.session.query(TopicProgress)\
        .filter_by(user_id=current_user.id, completed=False).limit(3).all()
    suggested_topics = [p.topic for p in incomplete_progress if p.topic]

    return render_template('dashboard/index.html',
                           total_topics=total_topics,
                           completed_topics=completed_topics,
                           progress_percent=progress_percent,
                           paper1_topics=paper1_topics,
                           paper2_topics=paper2_topics,
                           paper1_done=paper1_done,
                           paper2_done=paper2_done,
                           avg_score=avg_score,
                           best_score=best_score,
                           total_exams=len(exam_sessions),
                           recent_exams=recent_exams,
                           week_study=week_study,
                           total_study=current_user.total_study_minutes,
                           daily_data=daily_data,
                           score_trend=score_trend,
                           subject_progress=subject_progress,
                           suggested_topics=suggested_topics)

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    daily_data = []
    for i in range(13, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        mins = db.session.query(func.sum(StudySession.duration_minutes))\
            .filter(StudySession.user_id == current_user.id,
                    StudySession.session_date == day).scalar() or 0
        daily_data.append({'date': day.strftime('%b %d'), 'minutes': int(mins)})
    return jsonify(daily_data)
