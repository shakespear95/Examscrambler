# 🛡️ CCNA ExamGuard (Anti-Cheat Exam Engine & Grader)

A Flask-based assessment system engineered to eliminate academic dishonesty and reduce teacher grading overhead during networking exams (such as the Cisco CCNA). 

The platform guarantees fair difficulty across test-takers while ensuring that no two adjacent students encounter identical question orders or multiple-choice layouts.

---

## 🌟 Key Features

* **Balanced Difficulty Distribution:** Each exam samples equal quotas across difficulty tiers (Easy, Medium, Hard), ensuring every student receives a mathematically balanced assessment.
* **Two-Layer Anti-Cheating Engine:**
  * **Question Order Shuffling:** Questions are dynamically scrambled upon exam start.
  * **Option Choice Scrambling:** Multiple-choice options (A, B, C, D) are randomized per question per student.
* **Session Persistence:** Randomization states are locked into the database upon starting. Page refreshes, network disconnects, or browser crashes never change assigned questions or option layouts.
* **Instant Automated Grading:** Scores, percentage metrics, and full question-by-question rationales are generated the moment the student submits.
* **Teacher Gradebook Dashboard:** Live oversight panel displaying submission statuses, real-time completion states, and automated scoring breakdowns.

---

## 🏗️ Anti-Cheating Architecture

```
                 [ CCNA Question Pool ]
               /           |           \
      [Easy Tier]    [Medium Tier]    [Hard Tier]
               \           |           /
             [ Balanced Quota Sampler ]
                           │
             [ Question Order Scrambler ]
                           │
             [ Option Order Scrambler (A-D) ]
                           │
         [ Persist to Attempt & Answers Tables ]
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
  [Student Alice]                         [Student Bob]
  Q1: Subnetting (Opts: C, A, D, B)       Q1: OSPF (Opts: B, D, A, C)
  Q2: OSPF       (Opts: A, C, B, D)       Q2: VLANs (Opts: D, A, B, C)
```

---

## 🚀 Live Demo & Default Credentials

* **Live URL:** [https://examscrambler.fly.dev](https://examscrambler.fly.dev)

### Default Accounts (Pre-Seeded)

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Instructor** | `teacher@exam.com` | `admin123` | View gradebook, track submissions, monitor question bank |
| **Student** | `alice@exam.com` | `student123` | Take exam, review submitted score breakdowns |
| **Student** | `bob@exam.com` | `student123` | Take exam (isolated randomized layout) |
| **Student** | `charlie@exam.com` | `student123` | Take exam |

---

## 💻 Local Setup & Installation

Follow these steps to run the project locally for development or presentation.

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and Activate a Virtual Environment
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Starter Data
```bash
python seed.py
```

### 5. Launch the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📁 Project Directory Structure

```text
exam-system/
│
├── app.py                     # Application factory, routes, and auto-seeder logic
├── models.py                  # Database schemas (User, Question, Option, ExamAttempt)
├── seed.py                    # Seeder script for initial question bank and test users
├── requirements.txt           # Production & runtime dependencies
├── Dockerfile                 # Container specification for cloud deployment
├── fly.toml                   # Fly.io edge proxy and machine configuration
├── .gitignore                 # Excludes local databases, caches, and venv
│
├── .github/
│   └── workflows/
│       └── fly-deploy.yml     # Automated CI/CD deployment pipeline
│
├── static/
│   └── css/
│       └── style.css          # Custom interface styling
│
└── templates/
    ├── base.html              # Core navigation layout and alert banners
    ├── login.html             # Multi-role authentication view
    ├── student_dashboard.html # Lobby displaying instructions and previous attempts
    ├── exam.html              # Anti-cheat assessment interface
    ├── result.html            # Post-submission scoring breakdown
    └── admin_dashboard.html    # Teacher gradebook and monitoring console
```

---

## 🛠️ Technology Stack

* **Backend:** Python 3, Flask
* **Database & ORM:** SQLite, Flask-SQLAlchemy
* **Security & Auth:** Werkzeug (PBKDF2 SHA-256 password hashing), Flask session management
* **Frontend:** Jinja2 Templates, Bootstrap 5
* **Production Server:** Gunicorn WSGI
* **Hosting & CI/CD:** Docker, Fly.io, GitHub Actions# 🛡️ CCNA ExamGuard (Anti-Cheat Exam Engine & Grader)

A Flask-based assessment system engineered to eliminate academic dishonesty and reduce teacher grading overhead during networking exams (such as the Cisco CCNA). 

The platform guarantees fair difficulty across test-takers while ensuring that no two adjacent students encounter identical question orders or multiple-choice layouts.

---

## 🌟 Key Features

* **Balanced Difficulty Distribution:** Each exam samples equal quotas across difficulty tiers (Easy, Medium, Hard), ensuring every student receives a mathematically balanced assessment.
* **Two-Layer Anti-Cheating Engine:**
  * **Question Order Shuffling:** Questions are dynamically scrambled upon exam start.
  * **Option Choice Scrambling:** Multiple-choice options ($A, B, C, D$) are randomized per question per student.
* **Session Persistence:** Randomization states are locked into the database upon starting. Page refreshes, network disconnects, or browser crashes never change assigned questions or option layouts.
* **Instant Automated Grading:** Scores, percentage metrics, and full question-by-question rationales are generated the moment the student submits.
* **Teacher Gradebook Dashboard:** Live oversight panel displaying submission statuses, real-time completion states, and automated scoring breakdowns.

---

## 🏗️ Anti-Cheating Architecture


[ CCNA Question Pool ]
           /           |           \
  [Easy Tier]    [Medium Tier]    [Hard Tier]
           \           |           /
         [ Balanced Quota Sampler ]
                       │
         [ Question Order Scrambler ]
                       │
         [ Option Order Scrambler (A-D) ]
                       │
     [ Persist to Attempt & Answers Tables ]
                       │
   ┌───────────────────┴───────────────────┐
   ▼                                       ▼
[Student Alice]                         [Student Bob]
Q1: Subnetting (Opts: C, A, D, B)       Q1: OSPF (Opts: B, D, A, C)
Q2: OSPF       (Opts: A, C, B, D)       Q2: VLANs (Opts: D, A, B, C)


---

## 🚀 Live Demo & Default Credentials

* **Live URL:** [https://examscrambler.fly.dev](https://examscrambler.fly.dev)

### Default Accounts (Pre-Seeded)

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Instructor** | `teacher@exam.com` | `admin123` | View gradebook, track submissions, monitor question bank |
| **Student** | `alice@exam.com` | `student123` | Take exam, review submitted score breakdowns |
| **Student** | `bob@exam.com` | `student123` | Take exam (isolated randomized layout) |
| **Student** | `charlie@exam.com` | `student123` | Take exam |

---

## 💻 Local Setup & Installation

Follow these steps to run the project locally for development or presentation.

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/<your-repo-name>.git
cd <your-repo-name>
2. Create and Activate a Virtual Environment
Windows (PowerShell):

PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Initialize Database & Seed Starter Data
Bash
python seed.py
5. Launch the Application
Bash
python app.py
Open your browser and navigate to http://127.0.0.1:5000.

📁 Project Directory Structure
Plaintext
exam-system/
│
├── app.py                     # Application factory, routes, and auto-seeder logic
├── models.py                  # Database schemas (User, Question, Option, ExamAttempt)
├── seed.py                    # Seeder script for initial question bank and test users
├── requirements.txt           # Production & runtime dependencies
├── Dockerfile                 # Container specification for cloud deployment
├── fly.toml                   # Fly.io edge proxy and machine configuration
├── .gitignore                 # Excludes local databases, caches, and venv
│
├── .github/
│   └── workflows/
│       └── fly-deploy.yml     # Automated CI/CD deployment pipeline
│
├── static/
│   └── css/
│       └── style.css          # Custom interface styling
│
└── templates/
    ├── base.html              # Core navigation layout and alert banners
    ├── login.html             # Multi-role authentication view
    ├── student_dashboard.html # Lobby displaying instructions and previous attempts
    ├── exam.html              # Anti-cheat assessment interface
    ├── result.html            # Post-submission scoring breakdown
    └── admin_dashboard.html    # Teacher gradebook and monitoring console
🛠️ Technology Stack
Backend: Python 3, Flask

Database & ORM: SQLite, Flask-SQLAlchemy

Security & Auth: Werkzeug (PBKDF2 SHA-256 password hashing), Flask session management

Frontend: Jinja2 Templates, Bootstrap 5

Production Server: Gunicorn WSGI

Hosting & CI/CD: Docker, Fly.io, GitHub Actions