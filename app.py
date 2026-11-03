import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Question, Option, ExamAttempt, AttemptAnswer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-ccna-exam-2026'

# Use an absolute path for SQLite to prevent path issues in Docker/Fly.io
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'exam.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# -------------------------------------------------------------
# DATABASE INITIALIZATION & SEEDER
# -------------------------------------------------------------
def init_db():
    db.create_all()
    # If no users exist, populate default users and CCNA question bank
    if not User.query.first():
        print("Empty database detected. Initializing tables and CCNA dataset...")
        
        # 1. Create Default Users
        admin = User(email="teacher@exam.com", name="Prof. Davis", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        students_data = [
            ("alice@exam.com", "Alice Smith", "student123"),
            ("bob@exam.com", "Bob Johnson", "student123"),
            ("charlie@exam.com", "Charlie Brown", "student123"),
        ]
        for email, name, pwd in students_data:
            s = User(email=email, name=name, role="student")
            s.set_password(pwd)
            db.session.add(s)

        # 2. Seed Starter CCNA Questions
        ccna_questions = [
            # --- EASY ---
            {
                "topic": "OSI Model",
                "difficulty": "easy",
                "text": "At which layer of the OSI model does a standard network switch operate?",
                "options": [
                    ("Layer 2 (Data Link)", True),
                    ("Layer 3 (Network)", False),
                    ("Layer 1 (Physical)", False),
                    ("Layer 4 (Transport)", False),
                ]
            },
            {
                "topic": "IP Addressing",
                "difficulty": "easy",
                "text": "Which of the following is a private IPv4 address range according to RFC 1918?",
                "options": [
                    ("192.168.0.0/16", True),
                    ("172.33.0.0/16", False),
                    ("8.8.8.0/24", False),
                    ("11.0.0.0/8", False),
                ]
            },
            {
                "topic": "Cisco CLI",
                "difficulty": "easy",
                "text": "Which Cisco IOS command transitions the user from User EXEC to Privileged EXEC mode?",
                "options": [
                    ("enable", True),
                    ("configure terminal", False),
                    ("switchport mode access", False),
                    ("show run", False),
                ]
            },
            {
                "topic": "Transport Layer",
                "difficulty": "easy",
                "text": "Which protocol provides reliable, connection-oriented data transfer at Layer 4?",
                "options": [
                    ("TCP", True),
                    ("UDP", False),
                    ("ICMP", False),
                    ("ARP", False),
                ]
            },

            # --- MEDIUM ---
            {
                "topic": "Subnetting",
                "difficulty": "medium",
                "text": "How many usable host IP addresses are available in a subnet with a /27 prefix?",
                "options": [
                    ("30", True),
                    ("32", False),
                    ("62", False),
                    ("14", False),
                ]
            },
            {
                "topic": "VLANs & Trunking",
                "difficulty": "medium",
                "text": "What standard IEEE protocol is used to encapsulate VLAN tags on an Ethernet trunk link?",
                "options": [
                    ("802.1Q", True),
                    ("ISL", False),
                    ("802.1D", False),
                    ("802.3ad", False),
                ]
            },
            {
                "topic": "Routing Protocols",
                "difficulty": "medium",
                "text": "What administrative distance is assigned to OSPF routes by default on a Cisco router?",
                "options": [
                    ("110", True),
                    ("90", False),
                    ("120", False),
                    ("1", False),
                ]
            },
            {
                "topic": "STP",
                "difficulty": "medium",
                "text": "In Spanning Tree Protocol (STP), which switch becomes the Root Bridge?",
                "options": [
                    ("The switch with the lowest Bridge ID (Priority + MAC)", True),
                    ("The switch with the highest Bridge ID", False),
                    ("The switch with the fastest physical interface", False),
                    ("The switch configured as Default Gateway", False),
                ]
            },

            # --- HARD ---
            {
                "topic": "Subnetting",
                "difficulty": "hard",
                "text": "Given IP 172.16.45.14 / 22, what is the valid network address and broadcast address?",
                "options": [
                    ("Network: 172.16.44.0, Broadcast: 172.16.47.255", True),
                    ("Network: 172.16.45.0, Broadcast: 172.16.45.255", False),
                    ("Network: 172.16.40.0, Broadcast: 172.16.47.255", False),
                    ("Network: 172.16.44.0, Broadcast: 172.16.44.255", False),
                ]
            },
            {
                "topic": "OSPF",
                "difficulty": "hard",
                "text": "In a multi-access OSPF broadcast network, how is the Backup Designated Router (BDR) chosen?",
                "options": [
                    ("Highest OSPF priority, then highest Router ID (RID)", True),
                    ("Lowest OSPF priority, then lowest IP on active interface", False),
                    ("Lowest Router ID (RID) strictly", False),
                    ("First router configured with 'router ospf'", False),
                ]
            },
            {
                "topic": "Access Control Lists",
                "difficulty": "hard",
                "text": "What implicit rule is present at the very end of every Cisco standard and extended IPv4 ACL?",
                "options": [
                    ("deny ip any any", True),
                    ("permit ip any any", False),
                    ("deny tcp any any eq 80", False),
                    ("permit icmp any any", False),
                ]
            },
        ]

        for q_data in ccna_questions:
            q = Question(
                text=q_data["text"],
                topic=q_data["topic"],
                difficulty=q_data["difficulty"]
            )
            db.session.add(q)
            db.session.flush()

            for opt_text, is_correct in q_data["options"]:
                opt = Option(
                    question_id=q.id,
                    text=opt_text,
                    is_correct=is_correct
                )
                db.session.add(opt)

        db.session.commit()
        print("Database successfully initialized with users and CCNA questions.")

with app.app_context():
    init_db()


# -------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = get_current_user()
        if user and user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# -------------------------------------------------------------
# STUDENT ROUTES
# -------------------------------------------------------------
@app.route('/dashboard')
def student_dashboard():
    user = get_current_user()
    if not user or user.role != 'student':
        return redirect(url_for('login'))

    last_attempt = ExamAttempt.query.filter_by(user_id=user.id).order_by(ExamAttempt.id.desc()).first()
    return render_template('student_dashboard.html', user=user, last_attempt=last_attempt)


@app.route('/exam/start', methods=['POST'])
def start_exam():
    user = get_current_user()
    if not user or user.role != 'student':
        return redirect(url_for('login'))

    # If already in progress, resume the existing session
    active_attempt = ExamAttempt.query.filter_by(user_id=user.id, status='in_progress').first()
    if active_attempt:
        return redirect(url_for('take_exam', attempt_id=active_attempt.id))

    # Anti-Cheating: Sample balanced questions across difficulties
    easy_pool = Question.query.filter_by(difficulty='easy').all()
    medium_pool = Question.query.filter_by(difficulty='medium').all()
    hard_pool = Question.query.filter_by(difficulty='hard').all()

    selected_questions = (
        random.sample(easy_pool, min(2, len(easy_pool))) +
        random.sample(medium_pool, min(2, len(medium_pool))) +
        random.sample(hard_pool, min(2, len(hard_pool)))
    )

    # Scramble question display order
    random.shuffle(selected_questions)

    attempt = ExamAttempt(
        user_id=user.id,
        total_questions=len(selected_questions),
        status='in_progress'
    )
    db.session.add(attempt)
    db.session.flush()

    # Scramble options for each question and persist layout
    for order_idx, q in enumerate(selected_questions, start=1):
        opt_ids = [str(opt.id) for opt in q.options]
        random.shuffle(opt_ids)

        attempt_ans = AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            question_order=order_idx,
            shuffled_option_ids=",".join(opt_ids)
        )
        db.session.add(attempt_ans)

    db.session.commit()
    return redirect(url_for('take_exam', attempt_id=attempt.id))


@app.route('/exam/<int:attempt_id>', methods=['GET'])
def take_exam(attempt_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user.id and user.role != 'admin':
        flash('Unauthorized access to this exam attempt.', 'danger')
        return redirect(url_for('student_dashboard'))

    if attempt.status == 'completed':
        return redirect(url_for('exam_result', attempt_id=attempt.id))

    saved_answers = AttemptAnswer.query.filter_by(attempt_id=attempt.id).order_by(AttemptAnswer.question_order).all()

    exam_payload = []
    for sa in saved_answers:
        q = sa.question
        ordered_opt_ids = [int(i) for i in sa.shuffled_option_ids.split(',')]
        options_dict = {opt.id: opt for opt in q.options}
        ordered_options = [options_dict[i] for i in ordered_opt_ids if i in options_dict]

        exam_payload.append({
            'answer_record_id': sa.id,
            'question_order': sa.question_order,
            'topic': q.topic,
            'difficulty': q.difficulty,
            'text': q.text,
            'options': ordered_options,
            'selected_option_id': sa.selected_option_id
        })

    return render_template('exam.html', attempt=attempt, questions=exam_payload)


@app.route('/exam/<int:attempt_id>/submit', methods=['POST'])
def submit_exam(attempt_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user.id or attempt.status == 'completed':
        return redirect(url_for('student_dashboard'))

    saved_answers = AttemptAnswer.query.filter_by(attempt_id=attempt.id).all()
    correct_count = 0

    for sa in saved_answers:
        form_key = f"question_{sa.id}"
        chosen_opt_id = request.form.get(form_key)

        if chosen_opt_id:
            chosen_opt_id = int(chosen_opt_id)
            sa.selected_option_id = chosen_opt_id
            selected_option = Option.query.get(chosen_opt_id)
            if selected_option and selected_option.is_correct:
                correct_count += 1

    attempt.correct_count = correct_count
    attempt.total_questions = len(saved_answers)
    attempt.score = round((correct_count / len(saved_answers)) * 100, 1) if saved_answers else 0.0
    attempt.status = 'completed'
    attempt.submit_time = datetime.utcnow()

    db.session.commit()
    return redirect(url_for('exam_result', attempt_id=attempt.id))


@app.route('/exam/<int:attempt_id>/result')
def exam_result(attempt_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user.id and user.role != 'admin':
        return redirect(url_for('student_dashboard'))

    saved_answers = AttemptAnswer.query.filter_by(attempt_id=attempt.id).order_by(AttemptAnswer.question_order).all()

    breakdown = []
    for sa in saved_answers:
        q = sa.question
        chosen = Option.query.get(sa.selected_option_id) if sa.selected_option_id else None
        correct = Option.query.filter_by(question_id=q.id, is_correct=True).first()

        breakdown.append({
            'order': sa.question_order,
            'question': q.text,
            'topic': q.topic,
            'difficulty': q.difficulty,
            'chosen': chosen.text if chosen else "Unanswered",
            'is_correct': (chosen.is_correct if chosen else False),
            'correct_answer': correct.text if correct else ""
        })

    return render_template('result.html', attempt=attempt, breakdown=breakdown)


# -------------------------------------------------------------
# ADMIN / TEACHER ROUTES
# -------------------------------------------------------------
@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or user.role != 'admin':
        flash('Admin credentials required.', 'danger')
        return redirect(url_for('login'))

    students = User.query.filter_by(role='student').all()
    all_attempts = ExamAttempt.query.order_by(ExamAttempt.start_time.desc()).all()
    total_questions = Question.query.count()

    return render_template(
        'admin_dashboard.html',
        user=user,
        students=students,
        attempts=all_attempts,
        total_questions=total_questions
    )


if __name__ == '__main__':
    app.run(debug=True)