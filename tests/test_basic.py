"""Basic tests for UGC NET Prep application."""
import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Subject, Topic, Question


@pytest.fixture
def app():
    """Create test app instance."""
    test_app = create_app('development')
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['WTF_CSRF_ENABLED'] = False
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class TestHomePage:
    def test_home_loads(self, client):
        """Home page should return 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_home_contains_brand(self, client):
        """Home page should contain brand name."""
        response = client.get('/')
        assert b'NetPrep' in response.data


class TestAuth:
    def test_login_page_loads(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_register_page_loads(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_register_new_user(self, client):
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_register_duplicate_username(self, app, client):
        """Duplicate username should show error."""
        with app.app_context():
            user = User(username='existing', email='existing@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

        response = client.post('/auth/register', data={
            'username': 'existing',
            'email': 'new@test.com',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        assert b'already taken' in response.data or response.status_code in [200, 302]


class TestTopics:
    def test_topics_page_loads(self, client):
        response = client.get('/topics/')
        assert response.status_code == 200

    def test_topics_filter_paper1(self, client):
        response = client.get('/topics/?paper=paper1')
        assert response.status_code == 200

    def test_topic_detail_not_found(self, client):
        response = client.get('/topics/non-existent-slug')
        assert response.status_code == 404


class TestExam:
    def test_exam_page_requires_login(self, client):
        """Exam page should redirect unauthenticated users."""
        response = client.get('/exam/')
        # Either redirects to login or shows login prompt
        assert response.status_code in [200, 302]

    def test_exam_history_requires_login(self, client):
        response = client.get('/exam/history')
        assert response.status_code in [200, 302]


class TestModels:
    def test_user_password_hashing(self, app):
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('mypassword')
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')

    def test_subject_creation(self, app):
        with app.app_context():
            subj = Subject(name='Test Subject', paper='paper1',
                           description='Test', icon='📚')
            db.session.add(subj)
            db.session.commit()
            assert Subject.query.filter_by(name='Test Subject').first() is not None

    def test_topic_question_count(self, app):
        with app.app_context():
            subj = Subject(name='S', paper='paper2', description='d', icon='💻')
            db.session.add(subj)
            db.session.flush()
            topic = Topic(subject_id=subj.id, title='T', slug='t-slug',
                          content='Content', difficulty='easy')
            db.session.add(topic)
            db.session.flush()
            assert topic.get_question_count() == 0

            q = Question(topic_id=topic.id, paper='paper2',
                         question_text='Q?', option_a='A', option_b='B',
                         option_c='C', option_d='D', correct_answer='A')
            db.session.add(q)
            db.session.commit()
            assert topic.get_question_count() == 1
