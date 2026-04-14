from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    study_streak = db.Column(db.Integer, default=0)
    total_study_minutes = db.Column(db.Integer, default=0)

    topic_progress = db.relationship('TopicProgress', backref='user', lazy='dynamic')
    exam_sessions = db.relationship('ExamSession', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_overall_progress(self):
        total = TopicProgress.query.filter_by(user_id=self.id).count()
        completed = TopicProgress.query.filter_by(user_id=self.id, completed=True).count()
        return {'total': total, 'completed': completed,
                'percent': round((completed / total * 100) if total > 0 else 0)}

    def get_average_score(self):
        sessions = ExamSession.query.filter_by(user_id=self.id, completed=True).all()
        if not sessions:
            return 0
        return round(sum(s.score_percent for s in sessions) / len(sessions), 1)

    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    paper = db.Column(db.String(10), nullable=False)  # 'paper1' or 'paper2'
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='📚')
    color = db.Column(db.String(20), default='#4F46E5')
    order = db.Column(db.Integer, default=0)

    topics = db.relationship('Topic', backref='subject', lazy='dynamic',
                             order_by='Topic.order')

    def __repr__(self):
        return f'<Subject {self.name}>'


class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)  # Markdown content
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    estimated_minutes = db.Column(db.Integer, default=30)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship('Question', backref='topic', lazy='dynamic')
    user_progress = db.relationship('TopicProgress', backref='topic', lazy='dynamic')

    def get_question_count(self):
        return self.questions.count()

    def __repr__(self):
        return f'<Topic {self.title}>'


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, D
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='medium')
    paper = db.Column(db.String(10))  # paper1 or paper2
    year = db.Column(db.Integer)  # exam year if from past paper
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'topic_id': self.topic_id
        }

    def __repr__(self):
        return f'<Question {self.id}>'


class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paper = db.Column(db.String(10))  # paper1, paper2, or mixed
    title = db.Column(db.String(200))
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    score_percent = db.Column(db.Float, default=0.0)
    time_taken_seconds = db.Column(db.Integer, default=0)
    time_limit_seconds = db.Column(db.Integer, default=3600)
    completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    answers = db.relationship('ExamAnswer', backref='session', lazy='dynamic',
                              cascade='all, delete-orphan')

    def calculate_score(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 1)

    def get_grade(self):
        score = self.score_percent
        if score >= 85:
            return 'Excellent', '🏆'
        elif score >= 70:
            return 'Good', '🥈'
        elif score >= 55:
            return 'Average', '📘'
        else:
            return 'Needs Improvement', '📖'

    def format_time(self):
        m, s = divmod(self.time_taken_seconds, 60)
        return f"{m}m {s}s"

    def __repr__(self):
        return f'<ExamSession {self.id}>'


class ExamAnswer(db.Model):
    __tablename__ = 'exam_answers'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_answer = db.Column(db.String(1))  # A, B, C, D or None if skipped
    is_correct = db.Column(db.Boolean, default=False)
    time_spent_seconds = db.Column(db.Integer, default=0)

    question = db.relationship('Question')

    def __repr__(self):
        return f'<ExamAnswer {self.id}>'


class TopicProgress(db.Model):
    __tablename__ = 'topic_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    study_minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    last_studied = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'topic_id'),)

    def __repr__(self):
        return f'<TopicProgress user={self.user_id} topic={self.topic_id}>'


class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    session_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='study_sessions')
    topic = db.relationship('Topic')

    def __repr__(self):
        return f'<StudySession {self.id}>'
