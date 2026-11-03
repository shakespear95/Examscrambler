# 🛡️ CCNA ExamGuard (Anti-Cheat Exam Engine & Grader)

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


