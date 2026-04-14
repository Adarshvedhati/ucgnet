from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models import Question, ExamSession, ExamAnswer, Subject, Topic
import random
import json
from datetime import datetime

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/')
@login_required
def index():
    subjects = Subject.query.order_by(Subject.paper, Subject.order).all()
    recent_sessions = ExamSession.query.filter_by(
        user_id=current_user.id, completed=True
    ).order_by(ExamSession.completed_at.desc()).limit(5).all()
    return render_template('exam/index.html', subjects=subjects,
                           recent_sessions=recent_sessions)

@exam_bp.route('/start', methods=['POST'])
@login_required
def start():
    paper = request.form.get('paper', 'mixed')
    num_questions = int(request.form.get('num_questions', 25))
    time_limit = int(request.form.get('time_limit', 45))
    difficulty = request.form.get('difficulty', 'all')
    subject_ids = request.form.getlist('subjects')

    num_questions = min(max(num_questions, 5), 100)
    time_limit_seconds = time_limit * 60

    query = Question.query
    if paper != 'mixed':
        query = query.filter_by(paper=paper)
    if difficulty != 'all':
        query = query.filter_by(difficulty=difficulty)
    if subject_ids:
        topic_ids = [t.id for t in Topic.query.filter(
            Topic.subject_id.in_([int(s) for s in subject_ids])).all()]
        if topic_ids:
            query = query.filter(Question.topic_id.in_(topic_ids))

    all_questions = query.all()
    if len(all_questions) < 5:
        flash('Not enough questions available for the selected filters. Try different settings.', 'warning')
        return redirect(url_for('exam.index'))

    selected = random.sample(all_questions, min(num_questions, len(all_questions)))

    exam_session = ExamSession(
        user_id=current_user.id,
        paper=paper,
        title=f"Mock Exam - {paper.replace('paper', 'Paper ').title()} ({len(selected)} Qs)",
        total_questions=len(selected),
        time_limit_seconds=time_limit_seconds
    )
    db.session.add(exam_session)
    db.session.flush()

    # Store question order in session
    # ✅ FIX: append 'Z' so JavaScript parses this as UTC, not local time
    session[f'exam_{exam_session.id}_questions'] = [q.id for q in selected]
    session[f'exam_{exam_session.id}_start'] = datetime.utcnow().isoformat() + 'Z'

    db.session.commit()
    return redirect(url_for('exam.take', session_id=exam_session.id))

@exam_bp.route('/take/<int:session_id>')
@login_required
def take(session_id):
    exam_session = ExamSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()

    if exam_session.completed:
        return redirect(url_for('exam.results', session_id=session_id))

    question_ids = session.get(f'exam_{session_id}_questions', [])
    if not question_ids:
        flash('Exam session expired. Please start a new exam.', 'warning')
        return redirect(url_for('exam.index'))

    questions = []
    for qid in question_ids:
        q = Question.query.get(qid)
        if q:
            questions.append(q.to_dict())

    # Existing answers
    existing_answers = {a.question_id: a.selected_answer
                        for a in exam_session.answers}

    # ✅ FIX: also append 'Z' to the fallback so it is always UTC
    start_time = session.get(f'exam_{session_id}_start',
                             exam_session.started_at.isoformat() + 'Z')

    return render_template('exam/take.html',
                           exam_session=exam_session,
                           questions_json=json.dumps(questions),
                           existing_answers=json.dumps(existing_answers),
                           start_time=start_time)

@exam_bp.route('/submit/<int:session_id>', methods=['POST'])
@login_required
def submit(session_id):
    try:
        exam_session = ExamSession.query.filter_by(
            id=session_id, user_id=current_user.id).first_or_404()

        if exam_session.completed:
            return jsonify({"error": "Exam already submitted"}), 400

        # ✅ NEW CHECK
        start_time = session.get(f'exam_{session_id}_start')
        question_ids = session.get(f'exam_{session_id}_questions')

        if not start_time or not question_ids:
            return jsonify({
                "error": "Exam not started or session expired"
            }), 400

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)

        ExamAnswer.query.filter_by(session_id=session_id).delete()

        correct = 0

        for qid_str, selected in answers.items():
            qid = int(qid_str)
            question = Question.query.get(qid)

            if not question:
                continue

            is_correct = (selected == question.correct_answer)

            if is_correct:
                correct += 1

            db.session.add(ExamAnswer(
                session_id=session_id,
                question_id=qid,
                selected_answer=selected,
                is_correct=is_correct
            ))

        # Handle unanswered
        answered_ids = set(int(k) for k in answers.keys())

        for qid in question_ids:
            if qid not in answered_ids:
                db.session.add(ExamAnswer(
                    session_id=session_id,
                    question_id=qid,
                    selected_answer=None,
                    is_correct=False
                ))

        exam_session.correct_answers = correct
        exam_session.score_percent = exam_session.calculate_score()
        exam_session.time_taken_seconds = int(time_taken)
        exam_session.completed = True
        exam_session.completed_at = datetime.utcnow()  # ✅ fixed

        db.session.commit()

        # clear session
        session.pop(f'exam_{session_id}_questions', None)
        session.pop(f'exam_{session_id}_start', None)

        return jsonify({
            'status': 'ok',
            'redirect': url_for('exam.results', session_id=session_id)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
@exam_bp.route('/results/<int:session_id>')
@login_required
def results(session_id):
    exam_session = ExamSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()

    if not exam_session.completed:
        return redirect(url_for('exam.take', session_id=session_id))

    answers = ExamAnswer.query.filter_by(session_id=session_id).all()
    grade, grade_icon = exam_session.get_grade()

    # Stats
    answered = sum(1 for a in answers if a.selected_answer is not None)
    skipped = len(answers) - answered

    topic_stats = {}
    for ans in answers:
        if ans.question and ans.question.topic:
            t = ans.question.topic.title
            if t not in topic_stats:
                topic_stats[t] = {'correct': 0, 'total': 0}
            topic_stats[t]['total'] += 1
            if ans.is_correct:
                topic_stats[t]['correct'] += 1

    return render_template('exam/results.html',
                           exam_session=exam_session,
                           answers=answers,
                           grade=grade,
                           grade_icon=grade_icon,
                           answered=answered,
                           skipped=skipped,
                           topic_stats=topic_stats)

@exam_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    sessions = ExamSession.query.filter_by(
        user_id=current_user.id, completed=True
    ).order_by(ExamSession.completed_at.desc()).paginate(page=page, per_page=10)
    return render_template('exam/history.html', sessions=sessions)