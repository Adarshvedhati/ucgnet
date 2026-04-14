"""
UGC NET COMPLETE SYLLABUS SEEDER
Paper 1 + Computer Science Paper 2

Run:
python seed_data.py
"""

import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Subject, Topic, Question

app = create_app("development")


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


# ==========================================================
# PAPER 1 COMPLETE SYLLABUS
# ==========================================================

PAPER1_UNITS = {

"Teaching Aptitude":[
"Nature of teaching",
"Characteristics of learners",
"Factors affecting teaching",
"Methods of teaching",
"Levels of teaching",
"Evaluation systems",
"Teaching aids",
"Micro teaching",
"Team teaching"
],

"Research Aptitude":[
"Meaning of research",
"Types of research",
"Research methods",
"Research ethics",
"Sampling methods",
"Data collection techniques",
"Hypothesis formulation",
"Research report writing"
],

"Reading Comprehension":[
"Passage analysis",
"Understanding arguments",
"Inference making",
"Vocabulary understanding"
],

"Communication":[
"Communication process",
"Types of communication",
"Barriers of communication",
"Effective classroom communication"
],

"Reasoning":[
"Deductive reasoning",
"Inductive reasoning",
"Analogical reasoning",
"Logical puzzles",
"Statement and assumption",
"Statement and conclusion"
],

"Logical Reasoning":[
"Argument evaluation",
"Logical fallacies",
"Cause and effect",
"Venn diagrams"
],

"Data Interpretation":[
"Tables",
"Bar charts",
"Pie charts",
"Line graphs",
"Data analysis techniques"
],

"ICT":[
"Computer fundamentals",
"Internet basics",
"Email systems",
"Educational technology",
"Digital learning platforms",
"MOOCs"
],

"People Development and Environment":[
"Human development",
"Sustainable development",
"Environmental issues",
"Pollution control",
"Natural resources"
],

"Higher Education System":[
"Structure of higher education",
"UGC and regulatory bodies",
"Accreditation",
"Policies and governance",
"Research funding agencies"
]

}


# ==========================================================
# PAPER 2 COMPUTER SCIENCE COMPLETE SYLLABUS
# ==========================================================

PAPER2_UNITS = {

"Discrete Structures":[
"Logic and proof techniques",
"Sets and relations",
"Functions",
"Recurrence relations",
"Graph theory",
"Trees",
"Combinatorics"
],

"Computer System Architecture":[
"Digital logic",
"Number systems",
"Boolean algebra",
"Processor architecture",
"Pipelining",
"Memory hierarchy",
"Instruction set architecture"
],

"Programming and Data Structures":[
"Arrays",
"Linked lists",
"Stacks",
"Queues",
"Trees",
"Graphs",
"Hashing",
"Recursion"
],

"Algorithms":[
"Sorting algorithms",
"Searching algorithms",
"Divide and conquer",
"Dynamic programming",
"Greedy algorithms",
"Backtracking",
"Complexity analysis"
],

"Theory of Computation":[
"Finite automata",
"Regular expressions",
"Context free grammars",
"Pushdown automata",
"Turing machines",
"Computability",
"Complexity classes"
],

"Compiler Design":[
"Lexical analysis",
"Syntax analysis",
"Parsing techniques",
"Semantic analysis",
"Intermediate code generation",
"Code optimization"
],

"Operating Systems":[
"Process management",
"Threads",
"CPU scheduling",
"Deadlocks",
"Memory management",
"Virtual memory",
"File systems"
],

"Databases":[
"Relational model",
"SQL",
"Normalization",
"Transactions",
"Concurrency control",
"Query optimization"
],

"Computer Networks":[
"OSI model",
"TCP/IP",
"Routing protocols",
"Network security",
"Wireless networks"
],

"Software Engineering":[
"SDLC models",
"Agile methodology",
"Requirement analysis",
"Software testing",
"Design patterns",
"Software project management"
]

}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def create_subject(name):
    subject = Subject.query.filter_by(name=name).first()

    if not subject:
        subject = Subject(
            name=name,
            slug=slugify(name)
        )
        db.session.add(subject)
        db.session.commit()

    return subject


def create_topic(subject, topic_name):

    topic = Topic.query.filter_by(title=topic_name).first()

    if topic:
        return

    topic = Topic(
        title=topic_name,
        slug=slugify(topic_name),
        content=f"""
# {topic_name}

This topic is part of the **UGC NET syllabus**.

## Concept
Detailed explanation about **{topic_name}** will be generated dynamically
by the AI content generator.

## Key Points
• Definition  
• Important concepts  
• Examples  
• Applications  
• Previous year questions  

## For UGC NET
Focus on:
- conceptual understanding
- objective questions
- practical applications
"""
    )

    topic.subject = subject

    db.session.add(topic)


# ==========================================================
# SEEDING FUNCTION
# ==========================================================

def seed_paper1():

    print("Seeding Paper 1 syllabus...")

    for subject_name, topics in PAPER1_UNITS.items():

        subject = create_subject(subject_name)

        for topic in topics:
            create_topic(subject, topic)

    db.session.commit()


def seed_paper2():

    print("Seeding Paper 2 CS syllabus...")

    for subject_name, topics in PAPER2_UNITS.items():

        subject = create_subject(subject_name)

        for topic in topics:
            create_topic(subject, topic)

    db.session.commit()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    with app.app_context():

        print("Clearing existing topics...")
        Topic.query.delete()
        Subject.query.delete()

        db.session.commit()

        seed_paper1()
        seed_paper2()

        print("UGC NET FULL SYLLABUS SEEDED SUCCESSFULLY")