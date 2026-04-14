# 🎓 NetPrep — UGC NET IT & CS Preparation Platform

A full-stack Flask web application for UGC NET IT and Computer Science exam preparation with topic explanations, timed mock exams, and intelligent progress tracking.

---

## 🚀 Quick Start (3 Steps)

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1 — Install Dependencies
```bash
cd ugc_net_prep
pip install -r requirements.txt
```

### Step 2 — Seed the Database
```bash
python seed_data.py
```
This creates `ugcnet.db` and populates it with:
- 7 Paper 1 subjects + topics + questions
- 6 Paper 2 subjects + topics + questions
- 40+ practice questions with detailed explanations

### Step 3 — Run the App
```bash
python run.py
```

Open your browser at: **http://localhost:5000**

---

## 📁 Project Structure

```
ugc_net_prep/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── main.py          # Homepage and about
│   │   ├── auth.py          # Login, register, profile
│   │   ├── topics.py        # Topic study and notes
│   │   ├── exam.py          # Mock exam generator
│   │   └── dashboard.py     # Progress analytics
│   └── templates/
│       ├── base.html        # Shared layout and navbar
│       ├── index.html       # Landing page
│       ├── auth/            # Login, register, profile
│       ├── topics/          # Topic list and detail
│       ├── exam/            # Exam, results, history
│       └── dashboard/       # Progress dashboard
├── config.py                # App configuration
├── run.py                   # Entry point
├── seed_data.py             # Database seeder
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🗄️ Data Model

```
User           — registered students
  └── TopicProgress   — per-user topic completion & notes
  └── ExamSession     — mock exam records
        └── ExamAnswer    — per-question answers
  └── StudySession    — time logged studying

Subject        — e.g. "Data Structures", "Teaching Aptitude"
  └── Topic         — individual study topics with Markdown content
        └── Question    — MCQ with 4 options and explanation
```

---

## 📚 Content Coverage

### Paper 1 (General Aptitude)
| Subject | Topics |
|---------|--------|
| Teaching Aptitude | Nature of teaching, Methods, Evaluation |
| Research Aptitude | Types, Methods, Ethics |
| ICT in Education | Tools, E-learning, Digital literacy |
| Logical Reasoning | Deductive, Inductive, Fallacies |

### Paper 2 (IT & Computer Science)
| Subject | Topics |
|---------|--------|
| Data Structures & Algorithms | Arrays, Trees, Graphs, Sorting |
| Operating Systems | Scheduling, Memory, Deadlocks |
| Database Management | SQL, Normalization, Transactions |
| Computer Networks | OSI, TCP/IP, Routing, Security |
| Software Engineering | SDLC, Agile, Testing |
| Theory of Computation | Automata, Grammars, Complexity |

---

## ✨ Features

- **Rich Study Material** — Markdown-rendered topic pages with tables, code blocks
- **Study Timer** — Built-in stopwatch to log time per topic
- **Personal Notes** — Save notes per topic (persisted in DB)
- **Mark Complete** — Track completion status per topic
- **Mock Exam Generator**
  - Choose: Paper 1 / Paper 2 / Mixed
  - Set number of questions (5–100)
  - Set time limit (10min–3hr)
  - Filter by difficulty and subject
  - Countdown timer with auto-submit
- **Instant Results** — Score, grade, answer review with explanations
- **Progress Dashboard**
  - Overall and paper-wise progress bars
  - 14-day study activity chart
  - Score trend chart
  - Subject-level breakdown
  - Suggested next topics
- **Exam History** — Paginated history of all exams

---

## 🔧 Configuration

Create a `.env` file for production settings:

```env
SECRET_KEY=your-very-secret-key-change-this
DATABASE_URL=postgresql://user:password@localhost/ugcnet
FLASK_ENV=production
```

### Using PostgreSQL (Production)
```bash
pip install psycopg2-binary
```
Then set `DATABASE_URL` to your PostgreSQL connection string.

---

## 🗄️ Database Migrations

If you modify `models.py`:
```bash
flask db init         # First time only
flask db migrate -m "Description"
flask db upgrade
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/
```

---

## 📦 Adding More Questions

Edit `seed_data.py` and add to the `questions` list in any subject:

```python
{
    'question_text': 'Your question here?',
    'option_a': 'Option A',
    'option_b': 'Option B',
    'option_c': 'Option C',
    'option_d': 'Option D',
    'correct_answer': 'B',          # A, B, C or D
    'explanation': 'Why B is correct...',
    'difficulty': 'medium'          # easy, medium, hard
}
```

Then re-run: `python seed_data.py`

---

## 🚢 Deployment (Heroku)

```bash
echo "web: gunicorn run:app" > Procfile
pip install gunicorn
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python seed_data.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 3.0, Python 3.x |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Flask-Login |
| Migrations | Flask-Migrate (Alembic) |
| Markdown | Python-Markdown |
| Charts | Chart.js 4.4 |
| Icons | Font Awesome 6 |
| Fonts | Google Fonts (Playfair Display, DM Sans) |

---

## 📝 License

MIT License — free for educational use.

---

*Built with ❤️ for UGC NET aspirants. Good luck! 🍀*
