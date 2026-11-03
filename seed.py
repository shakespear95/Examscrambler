from app import app
from models import db, User, Question, Option

def seed_database():
    with app.app_context():
        # Reset and recreate tables
        db.drop_all()
        db.create_all()

        print("Creating users...")
        # 1 Admin / Instructor
        admin = User(email="teacher@exam.com", name="Prof. Davis", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        # 3 Demo Students
        students_data = [
            ("alice@exam.com", "Alice Smith", "student123"),
            ("bob@exam.com", "Bob Johnson", "student123"),
            ("charlie@exam.com", "Charlie Brown", "student123"),
        ]
        for email, name, pwd in students_data:
            s = User(email=email, name=name, role="student")
            s.set_password(pwd)
            db.session.add(s)

        print("Seeding CCNA questions...")
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
            db.session.flush()  # Populates q.id for child options

            for opt_text, is_correct in q_data["options"]:
                opt = Option(
                    question_id=q.id,
                    text=opt_text,
                    is_correct=is_correct
                )
                db.session.add(opt)

        db.session.commit()
        print("Database successfully seeded with users and CCNA questions!")

if __name__ == "__main__":
    seed_database()