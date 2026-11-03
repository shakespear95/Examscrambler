import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Question, Option, ExamAttempt, AttemptAnswer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-ccna-exam-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# -------------------------------------------------------------
# HELPER DECORATORS & FUNCTIONS
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

    # Check for existing attempts
    last_attempt = ExamAttempt.query.filter_by(user_id=user.id).order_by(ExamAttempt.id.desc()).first()
    return render_template('student_dashboard.html', user=user, last_attempt=last_attempt)


@app.route('/exam/start', methods=['POST'])
def start_exam():
    user = get_current_user()
    if not user or user.role != 'student':
        return redirect(url_for('login'))

    # If already in progress, resume it rather than re-randomizing
    active_attempt = ExamAttempt.query.filter_by(user_id=user.id, status='in_progress').first()
    if active_attempt:
        return redirect(url_for('take_exam', attempt_id=active_attempt.id))

    # Anti-Cheating & Balanced Distribution Algorithm:
    # Pick balanced quotas across difficulty tiers (e.g. 2 easy, 2 medium, 2 hard)
    easy_pool = Question.query.filter_by(difficulty='easy').all()
    medium_pool = Question.query.filter_by(difficulty='medium').all()
    hard_pool = Question.query.filter_by(difficulty='hard').all()

    # Take up to 2 from each category based on available questions
    selected_questions = (
        random.sample(easy_pool, min(2, len(easy_pool))) +
        random.sample(medium_pool, min(2, len(medium_pool))) +
        random.sample(hard_pool, min(2, len(hard_pool)))
    )

    # Scramble question display order
    random.shuffle(selected_questions)

    # Create new exam attempt
    attempt = ExamAttempt(
        user_id=user.id,
        total_questions=len(selected_questions),
        status='in_progress'
    )
    db.session.add(attempt)
    db.session.flush()  # Generates attempt.id

    # For each question, scramble option choices and lock them in database
    for order_idx, q in enumerate(selected_questions, start=1):
        opt_ids = [str(opt.id) for opt in q.options]
        random.shuffle(opt_ids)  # Scramble A, B, C, D order for this student

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

    # Retrieve all assigned questions in their saved randomized order
    saved_answers = AttemptAnswer.query.filter_by(attempt_id=attempt.id).order_by(AttemptAnswer.question_order).all()

    exam_payload = []
    for sa in saved_answers:
        q = sa.question
        # Reconstruct the shuffled options locked for this student
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

    # Auto-Grader Logic
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)