from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from werkzeug.utils import secure_filename

import os
import time
from urllib.parse import quote


app = Flask(__name__)
NOTICE_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "notice_files"
)

os.makedirs(
    NOTICE_UPLOAD_FOLDER,
    exist_ok=True
)
ASSIGNMENT_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "assignment_files"
)

os.makedirs(
    ASSIGNMENT_UPLOAD_FOLDER,
    exist_ok=True
)
CHAT_UPLOAD_FOLDER = os.path.join(app.root_path, "static", "chat_files")
os.makedirs(CHAT_UPLOAD_FOLDER, exist_ok=True)
app.config["CHAT_UPLOAD_FOLDER"] = CHAT_UPLOAD_FOLDER
# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.environ.get("SECRET_KEY", "college_portal_secret_key")


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)




# =========================================================
# PDF UPLOAD CONFIGURATION
# =========================================================

PDF_FOLDER = os.path.join(
    app.root_path,
    "static",
    "pdfs"
)

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

if not os.path.isdir(PDF_FOLDER):
    raise RuntimeError(
        "ERROR: 'static/pdfs' exists but it is not a folder. "
        "Delete the file named 'pdfs' and create a folder named 'pdfs'."
    )

app.config["PDF_FOLDER"] = PDF_FOLDER


# =========================================================
# STUDENT TABLE
# =========================================================

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    roll_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    class_name = db.Column(
        db.String(50),
        nullable=False
    )

    year = db.Column(
        db.String(30),
        nullable=False,
        default="3rd Year"
    )

    batch = db.Column(
        db.String(30),
        nullable=False,
        default="2024-2028"
    )

    department = db.Column(
        db.String(100),
        nullable=False,
        default="Computer Science and Engineering"
    )

    # CSE-A / CSE-B / ECE
    group_name = db.Column(db.String(20), nullable=False, default="CSE-A")


# =========================================================
# TEACHER TABLE
# =========================================================

class Teacher(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    # Teacher can work with all three groups; current login chooses one.
    groups = db.Column(db.String(100), nullable=False, default="CSE-A,CSE-B,ECE,AIML")


# =========================================================
# ADMIN TABLE
# =========================================================

class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )


# =========================================================
# ATTENDANCE TABLE
# =========================================================

class Attendance(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    attendance_date = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False
    )

    student = db.relationship(
        "Student",
        backref="attendance_records"
    )

    teacher = db.relationship(
        "Teacher",
        backref="attendance_records"
    )


# =========================================================
# MARKS TABLE
# =========================================================

class Marks(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    internal = db.Column(
        db.Integer,
        nullable=False
    )

    external = db.Column(
        db.Integer,
        nullable=False
    )

    student = db.relationship(
        "Student",
        backref="marks_records"
    )
# =========================================================
# ASSIGNMENT TABLE
# =========================================================

class Assignment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    due_date = db.Column(
        db.String(20),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False
    )

    teacher = db.relationship(
        "Teacher",
        backref="assignments"
    )

    group_name = db.Column(db.String(20), nullable=False, default="CSE-A")

# =========================================================
# PDF TABLE
# =========================================================

class PDF(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(200),
        nullable=False
    )

    original_filename = db.Column(
        db.String(200),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False,
        default="Study Material"
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False
    )

    upload_date = db.Column(
        db.String(20),
        nullable=False
    )

    teacher = db.relationship(
        "Teacher",
        backref="pdf_files"
    )

    group_name = db.Column(db.String(20), nullable=False, default="CSE-A")
# =========================================================
# TIMETABLE DATA
# =========================================================

class TimetableData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    monday = db.Column(db.Text, nullable=False)
    tuesday = db.Column(db.Text, nullable=False)
    wednesday = db.Column(db.Text, nullable=False)
    thursday = db.Column(db.Text, nullable=False)
    friday = db.Column(db.Text, nullable=False)
    saturday = db.Column(db.Text, nullable=False)
    group_name = db.Column(db.String(20), nullable=False, default="ALL")


# =========================================================
# ADMIN NOTIFICATION TABLE
# =========================================================

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    actor_role = db.Column(db.String(20), nullable=False, default="system")
    group_name = db.Column(db.String(20), nullable=False, default="ALL")


class PortalEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_name = db.Column(db.String(30), nullable=False, default="ALL")
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    actor_role = db.Column(db.String(20), nullable=False, default="system")
    group_name = db.Column(db.String(20), nullable=False, default="ALL")
    event_type = db.Column(db.String(30), nullable=False, default="update")


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_name = db.Column(db.String(100), nullable=False, index=True)
    sender_role = db.Column(db.String(20), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=True)
    attachment_name = db.Column(db.String(255), nullable=True)
    attachment_original_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


def notify_portals(message, actor_role="system", group_name="ALL", event_type="update", year_name=None):
    year_name = year_name or session.get("year_name") or "ALL"
    db.session.add(PortalEvent(message=message, actor_role=actor_role, group_name=group_name, year_name=year_name, event_type=event_type))


def notify_admin(message, actor_role="system", group_name="ALL"):
    db.session.add(Notification(message=message, actor_role=actor_role, group_name=group_name))
    notify_portals(message, actor_role, group_name, "update")


# =========================================================
# STUDENT DATA
# =========================================================

students_data = [

    # =========================
    # CSE-A
    # =========================

    ("Y24CSE279001", "Abdul Sajida", "sajida001", "279001", "CSE-A"),
    ("Y24CSE279002", "Abu Taib", "taib002", "279002", "CSE-A"),
    ("Y24CSE279003", "Alluri Revakith Venkata Kumar", "kumar003", "279003", "CSE-A"),
    ("Y24CSE279004", "Aremanda Pujitha", "pujitha004", "279004", "CSE-A"),
    ("Y24CSE279005", "Atta Krishnam Naidu", "naidu005", "279005", "CSE-A"),
    ("Y24CSE279006", "Baipilli Gohini", "gohini006", "279006", "CSE-A"),
    ("Y24CSE279007", "Balagam Sri Lakshmi", "lakshmi007", "279007", "CSE-A"),
    ("Y24CSE279008", "Balagam Yohanu", "yohanu008", "279008", "CSE-A"),
    ("Y24CSE279009", "Balusupalli Anand Babu", "babu009", "279009", "CSE-A"),
    ("Y24CSE279010", "Basheerunisa", "basheerunisa010", "279010", "CSE-A"),
    ("Y24CSE279011", "Battula Gagan Chandra Moses", "moses011", "279011", "CSE-A"),
    ("Y24CSE279012", "Battula Ramu", "ramu012", "279012", "CSE-A"),
    ("Y24CSE279013", "Behara Gyaneswara Rao", "rao013", "279013", "CSE-A"),
    ("Y24CSE279014", "Bokinala Nikhil Babu", "babu014", "279014", "CSE-A"),
    ("Y24CSE279015", "Bon Kavya", "kavya015", "279015", "CSE-A"),
    ("Y24CSE279016", "Buraga Rohan Kumar", "kumar016", "279016", "CSE-A"),

    ("Y24CSE279018", "Chebathina Raghavendra", "raghavendra018", "279018", "CSE-A"),
    ("Y24CSE279019", "Chinnam Praneeth", "praneeth019", "279019", "CSE-A"),
    ("Y24CSE279020", "Chitajallu Vennela Sreya", "sreya020", "279020", "CSE-A"),
    ("Y24CSE279021", "Choragudi Sahith Babu", "babu021", "279021", "CSE-A"),
    ("Y24CSE279022", "Dalayi Devi Sri Deepa", "deepa022", "279022", "CSE-A"),
    ("Y24CSE279023", "Dandamudi Srivalli", "srivalli023", "279023", "CSE-A"),
    ("Y24CSE279024", "Dasari Naga Navya Sri", "sri024", "279024", "CSE-A"),
    ("Y24CSE279025", "Davu Nari Vardhani", "vardhani025", "279025", "CSE-A"),
    ("Y24CSE279026", "Deevi Syam Nikhil", "nikhil026", "279026", "CSE-A"),
    ("Y24CSE279027", "Deshik Badrachalam", "badrachalam027", "279027", "CSE-A"),
    ("Y24CSE279028", "Erikipati Akshaya", "akshaya028", "279028", "CSE-A"),
    ("Y24CSE279029", "Faruk Abdul", "abdul029", "279029", "CSE-A"),
    ("Y24CSE279030", "Gara Karthik", "karthik030", "279030", "CSE-A"),
    ("Y24CSE279031", "Gedala Naga Bhavani Anuradha", "anuradha031", "279031", "CSE-A"),
    ("Y24CSE279032", "Goli Venkata Padmavathi", "padmavathi032", "279032", "CSE-A"),
    ("Y24CSE279033", "Gosala Charishma", "charishma033", "279033", "CSE-A"),
    ("Y24CSE279034", "Gudapati Surendra", "surendra034", "279034", "CSE-A"),
    ("Y24CSE279035", "Gudaru Kalyani", "kalyani035", "279035", "CSE-A"),
    ("Y24CSE279036", "Irigi Harish", "harish036", "279036", "CSE-A"),
    ("Y24CSE279037", "Jakka Rama Venkata Aditya", "aditya037", "279037", "CSE-A"),

    ("Y24CSE279039", "Kalidindi Bhogesh", "bhogesh039", "279039", "CSE-A"),
    ("Y24CSE279040", "Kalyanapu Shyam Prasad", "prasad040", "279040", "CSE-A"),
    ("Y24CSE279041", "Kamapalli Mohammad Muniaf", "muniaf041", "279041", "CSE-A"),
    ("Y24CSE279042", "Kambhampati Madhu Babu", "babu042", "279042", "CSE-A"),
    ("Y24CSE279043", "Kanagala Naga Jayanthi", "jayanthi043", "279043", "CSE-A"),
    ("Y24CSE279044", "Kasi Lasya Sri Lalitha", "lalitha044", "279044", "CSE-A"),
    ("Y24CSE279045", "Katragadda Venkata Pavan Kumar", "kumar045", "279045", "CSE-A"),
    ("Y24CSE279046", "Katyala Lakshmanarao", "lakshmanarao046", "279046", "CSE-A"),
    ("Y24CSE279047", "Kayala Vyshnavi", "vyshnavi047", "279047", "CSE-A"),
    ("Y24CSE279048", "Kodeti Lakshmana Chandra", "chandra048", "279048", "CSE-A"),
    ("Y24CSE279049", "Kolikonda Tharun Kumar", "kumar049", "279049", "CSE-A"),
    ("Y24CSE279050", "Kommukuri Vardhan", "vardhan050", "279050", "CSE-A"),
    ("Y24CSE279051", "Kompalli Pavani Sai Sri", "sri051", "279051", "CSE-A"),
    ("Y24CSE279052", "Kondeti Neelima", "neelima052", "279052", "CSE-A"),
    ("Y24CSE279053", "Kondisetti Likitha", "likitha053", "279053", "CSE-A"),
    ("Y24CSE279054", "Konka Nikhil", "nikhil054", "279054", "CSE-A"),
    ("Y24CSE279055", "Kotnani Vinay", "vinay055", "279055", "CSE-A"),
    ("Y24CSE279056", "Kunchala Manoj Kumar", "kumar056", "279056", "CSE-A"),
    ("Y24CSE279057", "Likitha Kanchara", "kanchara057", "279057", "CSE-A"),
    ("Y24CSE279058", "Lokavarapu Hemalatha", "hemalatha058", "279058", "CSE-A"),
    ("Y24CSE279059", "Mahadevu Nageswararao", "nageswararao059", "279059", "CSE-A"),
    ("Y24CSE279060", "Manepalli Lokavinay Manikanta", "manikanta060", "279060", "CSE-A"),

    # =========================
    # CSE-B
    # =========================

    ("Y24CSE279061", "MANGALAPUDI MOHAN KUMAR", "kumar061", "279061", "CSE-B"),
    ("Y24CSE279062", "MARAPAKA SRESHA", "sresha062", "279062", "CSE-B"),
    ("Y24CSE279063", "MATHE VARDHAN", "vardhan063", "279063", "CSE-B"),
    ("Y24CSE279064", "MEESALA NITHIN", "nithin064", "279064", "CSE-B"),
    ("Y24CSE279065", "METTELA HARISH YADAV", "yadav065", "279065", "CSE-B"),
    ("Y24CSE279066", "MIRIYALA LOKESH", "lokesh066", "279066", "CSE-B"),
    ("Y24CSE279067", "MOTRU SASIKANTH", "sasikanth067", "279067", "CSE-B"),
    ("Y24CSE279068", "MUDAMANCHU RAJESH", "rajesh068", "279068", "CSE-B"),
    ("Y24CSE279069", "MUDUGU RAMYA", "ramya069", "279069", "CSE-B"),
    ("Y24CSE279070", "MUDUNURI ABHINAV", "abhinav070", "279070", "CSE-B"),
    ("Y24CSE279071", "MUNGANDA CHARAN KARTHIK", "karthik071", "279071", "CSE-B"),
    ("Y24CSE279072", "MUNIPALLI SIDDHARDA", "siddharda072", "279072", "CSE-B"),
    ("Y24CSE279073", "MURARI PREMANANDAM", "premanandam073", "279073", "CSE-B"),
    ("Y24CSE279074", "NAKKA PRAVEEN", "praveen074", "279074", "CSE-B"),

    ("Y24CSE279076", "NUTANGI SUBHASHINI", "subhashini076", "279076", "CSE-B"),
    ("Y24CSE279077", "PADAMATI SRI SAI DEEPAK RAJ", "raj077", "279077", "CSE-B"),
    ("Y24CSE279078", "PALAGANI RAMYA", "ramya078", "279078", "CSE-B"),
    ("Y24CSE279079", "PAMARTHI SAI SREE VENKATA SHANMUKHA", "shanmukha079", "279079", "CSE-B"),
    ("Y24CSE279080", "PANDIRI JAGADEESH", "jagadeesh080", "279080", "CSE-B"),
    ("Y24CSE279081", "PARAMESH NIRMALA DEVI NIKITHA", "nikitha081", "279081", "CSE-B"),
    ("Y24CSE279082", "PARASA ROHITH", "rohith082", "279082", "CSE-B"),
    ("Y24CSE279083", "PATIBANDLA CHIRISHMA", "chirishma083", "279083", "CSE-B"),
    ("Y24CSE279084", "PILLA CHARANMAI", "charanmai084", "279084", "CSE-B"),
    ("Y24CSE279085", "POLIPILLI PAWAN KUMAR", "kumar085", "279085", "CSE-B"),
    ("Y24CSE279086", "PONUGOTI STEEPHEN", "steephen086", "279086", "CSE-B"),

    ("Y24CSE279088", "PULI NAVYA SREE", "sree088", "279088", "CSE-B"),
    ("Y24CSE279089", "PULI YAMINI", "yamini089", "279089", "CSE-B"),
    ("Y24CSE279090", "RAMISETTI VENKATANADH", "venkatanadh090", "279090", "CSE-B"),
    ("Y24CSE279091", "RAVURI JYOTHI", "jyothi091", "279091", "CSE-B"),
    ("Y24CSE279092", "ROTHULA VENKATA KUMAR", "kumar092", "279092", "CSE-B"),
    ("Y24CSE279093", "SABA FATHEMA", "fathema093", "279093", "CSE-B"),
    ("Y24CSE279094", "SEELA VENKATA TEJA", "teja094", "279094", "CSE-B"),
    ("Y24CSE279095", "SHAIK ABBAS VALI", "vali095", "279095", "CSE-B"),
    ("Y24CSE279096", "SHAIK ABDULLA", "abdulla096", "279096", "CSE-B"),
    ("Y24CSE279097", "SHAIK NAGULMEERA", "nagulmeera097", "279097", "CSE-B"),
    ("Y24CSE279098", "SURISETTI RAMAKRISHNA", "ramakrishna098", "279098", "CSE-B"),
    ("Y24CSE279099", "SYED GULAME RASOOL", "rasool099", "279099", "CSE-B"),
    ("Y24CSE279100", "SYKAM BHAVYA", "bhavya100", "279100", "CSE-B"),
    ("Y24CSE279101", "THAMMU MANI SANKAR VENKATA GANESH", "ganesh101", "279101", "CSE-B"),
    ("Y24CSE279102", "THIPPANA SANTHOSH", "santhosh102", "279102", "CSE-B"),
    ("Y24CSE279103", "THOKALA SAIDULU RAJU", "raju103", "279103", "CSE-B"),
    ("Y24CSE279104", "TIKKISETTY RAMYA SREE LAKSHMI", "lakshmi104", "279104", "CSE-B"),
    ("Y24CSE279105", "UNDAPALLI KEERTHI", "keerthi105", "279105", "CSE-B"),
    ("Y24CSE279106", "VAYYAVURU BHAVANA", "bhavana106", "279106", "CSE-B"),
    ("Y24CSE279107", "VEMU VAMSI KUMAR", "kumar107", "279107", "CSE-B"),
    ("Y24CSE279108", "YANNA SRINIVAS", "srinivas108", "279108", "CSE-B"),
    ("Y24CSE279109", "YARAGORLA GOPI", "gopi109", "279109", "CSE-B"),
    ("Y24CSE279110", "YARASURI SURYA NAGA SAI CHANDU", "chandu110", "279110", "CSE-B"),
    
]



# =========================================================
# LATERAL + ECE STUDENTS
# =========================================================
additional_students_data = [('L25CSE279001', 'YASWANTH', 'yaswanth', '279001', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279002', 'MEGANA', 'megana', '279002', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279003', 'SINDHU', 'sindhu', '279003', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279004', 'TRIVENI', 'triveni', '279004', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279005', 'SHARON', 'sharon', '279005', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279006', 'RAJESWARI', 'rajeswari', '279006', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279007', 'MAHESH', 'mahesh', '279007', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279008', 'CHIRANJEEVI', 'chiranjeevi', '279008', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279009', 'PAVAN KUMAR', 'pavan kumar', '279009', 'CSE-A', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279010', 'JANAKIRAM', 'JANAKIRAM', '279010', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279011', 'AMRUTHA VARSHINI', 'AMRUTHA VARSHINI', '279011', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279012', 'CHANDRA KANTH', 'CHANDRA KANTH', '279012', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279013', 'THARANGINI', 'THARANGINI', '279013', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279014', 'KEERTHANA', 'KEERTHANA', '279014', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279015', 'YAMINI', 'YAMINI', '279015', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279016', 'SRILEKHA', 'SRILEKHA', '279016', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279017', 'JYOYH SWAROOP', 'JYOYH SWAROOP', '279017', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279018', 'MEGHANADHAM', 'MEGHANADHAM', '279018', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279019', 'JASWANTH', 'JASWANTH', '279019', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279020', 'UDAI CHANDHRA', 'UDAI CHANDHRA', '279020', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279021', 'SHARATH KUMAR', 'SHARATH KUMAR', '279021', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279022', 'PREM TEJA', 'PREM TEJA', '279022', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279023', 'NEERAJA', 'NEERAJA', '279023', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279024', 'RAMESH', 'RAMESH', '279024', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279025', 'VENKATA RATNAM', 'VENKATA RATNAM', '279025', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279026', 'VENKATESH', 'VENKATESH', '279026', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25CSE279027', 'CHANDRA SEKHAR', 'CHANDRA SEKHAR', '279027', 'CSE-B', '3rd Year', '2025-2027', 'Computer Science and Engineering'), ('L25ECE279001', 'ADABALA MAHESWARA GANGA SATYA ABHILASH', 'adabala', '279001', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279002', 'BORRASANTHOSHKUMAR', 'borrasanthoskumar', '279002', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279003', 'CHATARAJU PALLI SRI YAMINI', 'chataraju', '279003', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279004', 'CHATLAGADDA PRADEEP', 'chatlagadda', '279004', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279005', 'CHILUKOTI KOMALESWARI', 'chilukoti', '279005', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279006', 'CHINTAGUNTA GANI LAKSHMI', 'chintagunta', '279006', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279007', 'CHODAVARAPU CHAITANYA', 'chodavarapu', '279007', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279008', 'DALAYI YOGESWAR', 'dalayi', '279008', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279009', 'GOLAGANA DINESH', 'golagana', '279009', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279010', 'KATUKURI AJAYKUMAR', 'katukuri', '279010', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279011', 'KOTA PARAMESH', 'kota', '279011', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279012', 'KOUTHARAPU DINESH NAGA SURYA', 'koutharapu', '279012', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279013', 'KURUPUDI VENKATA GANESH', 'kurupudi', '279013', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279014', 'MASA CHERISHMA', 'masa', '279014', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279015', 'MEDIDA SWATHI', 'medida', '279015', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279016', 'MERUGU BHAGYA REKHA', 'merugu', '279016', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279017', 'MODDU RAJESH', 'moddu', '279017', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279018', 'MUPPIDI ENOS', 'muppidi', '279018', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279019', 'PAILA NITESH', 'paila', '279019', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279020', 'PATHIVADA THARUN', 'pathivada', '279020', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279021', 'PEDAPATI BHAGYA SREE', 'pedapati', '279021', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279022', 'PIRATLA VASAVYA', 'piratla', '279022', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279023', 'SIRIPURAPU AMRUTHA', 'siripurapu', '279023', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279024', 'SRUNGARAPU BHARGAV', 'srungarapu', '279024', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279025', 'SUMALA KARTHIK', 'sumala', '279025', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279026', 'TERLI UMESH CHANDU', 'terli', '279026', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279027', 'THIPPUGARI SRILAKSHMI NARASIMHA REDDY', 'thippugari', '279027', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279028', 'VALUROUTHU KIRTANA', 'valurouthu', '279028', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279029', 'VELPULA PRASANNA', 'velpula', '279029', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('L25ECE279030', 'YANDRA KARTHIK KUMAR', 'yandra', '279030', 'ECE', '3rd Year', '2025-2027', 'Electronics and Communication Engineering'), ('Y24ECE279001', 'ALLA KRISHNA CHAITANYA', 'alla', '279001', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279002', 'APPANABHOTLA KEDARA DATTA', 'appanabhotla', '279002', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279003', 'BODDETI RAMESH', 'boddeti', '279003', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279004', 'BOKKA PRAVEEN KUMAR', 'bokka', '279004', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279005', 'BYREDDY NAGANJALI', 'byreddy', '279005', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279006', 'CHALAMALASETTI LOHITHA LAKSHMI', 'chalamalasetti', '279006', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279007', 'CHALAMALASETTY LAKSHMI GANESH', 'chalamalasetty', '279007', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279008', 'CHANDIKA BEULAH', 'chandika', '279008', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279009', 'CHILLARA SANTOSH BABU', 'chillara', '279009', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279010', 'CHORAGUDI MANOJ KUMAR', 'choragudi', '279010', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279011', 'DANYASI MYTHRI', 'danyasi', '279011', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279012', 'EJJADA KUMAR', 'ejjada', '279012', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279013', 'GORRIPARTI DEVA RAJESH BABU', 'gorriparti', '279013', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279014', 'GUNTURU RANJITH KUMAR', 'gunturu', '279014', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279015', 'JONNALAGADDA LAKSHMI SIVA NAGA KISHORE', 'jonnalagadda', '279015', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279016', 'KANKIPATI JESSICA', 'kankipati', '279016', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279017', 'KAYAM SUDHESHNA', 'kayam', '279017', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279018', 'KOKKANTI GANESH', 'kokkanti', '279018', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279019', 'KORUPROLU SRI HARI PRAKASH', 'koruprolu', '279019', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279020', 'MAHADASU SAI DINESH', 'mahadasu', '279020', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279021', 'MANDALANENI MAHENDRA PRUDVI', 'mandalaneni', '279021', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279022', 'MANIKANTA DURGA PRASAD MARETI', 'manikanta', '279022', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279023', 'MERUGU RAKESH', 'rakesh', '279023', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279024', 'MOHAMMAD AMEEN RABBANI', 'mohammad024', '279024', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279025', 'MOHAMMAD TABASUM FATHIMA', 'mohammad025', '279025', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279026', 'ODUGU PRAKASH', 'odugu', '279026', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279027', 'PASUMARTHI DEEPIKA', 'pasumarthi', '279027', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279028', 'PENDEM JAGADEESWAR', 'pendem', '279028', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279029', 'PIRIYA SAMPATH', 'piriya', '279029', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279030', 'POTUNURU VASANTH KUMAR', 'potunuru', '279030', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279031', 'TENALI CHARAN', 'tenali', '279031', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279032', 'THANAMCHINTALA SUNNY', 'thanamchintala', '279032', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279033', 'THANAMCHINTHALA NEHEMIA', 'thanamchinthala', '279033', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279034', 'TULUGU CHINNAMOHAN', 'tulugu', '279034', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279035', 'UPPALAPU SAI SUJITH', 'uppalapu', '279035', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279036', 'VANNEMREDDI VISWANTH ABHIRAM', 'vannemreddi', '279036', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279037', 'VANTIPALLI REVANTH VENKATA KUMAR', 'vantipalli', '279037', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering'), ('Y24ECE279038', 'VEERA NAGA VAMSI', 'veera', '279038', 'ECE', '1st Year', '2024-2028', 'Electronics and Communication Engineering')]

# =========================================================
# NOTICE TABLE
# =========================================================

class Notice(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    notice_date = db.Column(
        db.String(20),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False
    )

    teacher = db.relationship(
        "Teacher",
        backref="notices"
    )

    group_name = db.Column(db.String(20), nullable=False, default="CSE-A")
    # =========================================================
# NOTICE ATTACHMENTS
# =========================================================

class NoticeAttachment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    notice_id = db.Column(
        db.Integer,
        db.ForeignKey("notice.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(300),
        nullable=False
    )

    original_filename = db.Column(
        db.String(300),
        nullable=False
    )

    file_type = db.Column(
        db.String(20),
        nullable=False
    )

    notice = db.relationship(
        "Notice",
        backref="attachments"
    )


# =========================================================
# SQLITE MIGRATION HELPERS
# =========================================================
def ensure_column(table, column, definition):
    rows = db.session.execute(db.text(f"PRAGMA table_info({table})")).fetchall()
    if column not in [r[1] for r in rows]:
        db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))


# =========================================================
# CREATE DATABASE + DEFAULT ACCOUNTS
# =========================================================
# =========================================================
# 2ND YEAR AIML STUDENTS
# =========================================================
aiml_2nd_year_data = [('Y25AIML279001', 'AKURI POOJITHA', 'poojitha', '279001', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279002', 'BANDI DEEKSHITHA', 'deekshitha', '279002', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279003', 'BEZAWADA VEERA VENKATA NAGA VINAY', 'vinay', '279003', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279004', 'CHENNAKESAVULA HEMANTH', 'hemanth', '279004', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279005', 'CHINTALA VENKATESWARLU', 'venkateswarlu', '279005', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279006', 'DIRISINALA KAVYA', 'kavya', '279006', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279007', 'DUDDU VINEELA', 'vineela', '279007', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279008', 'EDADALA REDDY CHARAN', 'charan', '279008', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279009', 'GADDETI CHANDU', 'chandu', '279009', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279010', 'GADIDESI SIDDHARTHA', 'siddhartha', '279010', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279011', 'GUNURI DURGA PRASAD', 'prasad', '279011', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279012', 'IJLLELLA SURESH BABU', 'babu', '279012', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279013', 'KALI HARSHA', 'harsha', '279013', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279014', 'KANCHERLA TONI HARSHA', 'toniharsha', '279014', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279015', 'KANCHERLAPALLI VEERA VENKATA NAGA ASHOK', 'ashok', '279015', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279016', 'KOTAPATI LAKSHMI REDDY', 'lakshmireddy', '279016', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279017', 'LAM SANDEEP', 'sandeep', '279017', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279018', 'MADDILA CHAKRAHAASINI', 'chakrahaasini', '279018', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279019', 'MANJUNATH GARI KUMUDA', 'kumuda', '279019', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279020', 'MAREEDU UPENDRA', 'upendra', '279020', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279021', 'MEDEPALLI SANDEEP', 'sandeep021', '279021', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279022', 'MOLUGUMATI RAJESH', 'rajesh', '279022', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279023', 'NAIDU JESSY KUMAR', 'jessykumar', '279023', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279024', 'NIMAMALA RANJITH', 'ranjith', '279024', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279025', 'ODUGU BHANU', 'bhanu', '279025', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279026', 'ONTERU NAGA NIVAS', 'nivas', '279026', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279027', 'PEKETI MADHAV', 'madhav', '279027', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279028', 'PODILI VANESHA', 'vanesha', '279028', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279029', 'RAMACHANDRAPPA GARI HARSHAVARDHAN', 'harshavardhan', '279029', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279030', 'SARIMALLA LAVANYA', 'lavanya', '279030', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279031', 'SHAIK KARISHMA', 'karishma', '279031', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279032', 'SHAIK REHANA BEGUM', 'rehanabegum', '279032', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279033', 'SHAIK SEEMA KOWSAR', 'seemakowsar', '279033', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279034', 'SHAIK TAHASEEN', 'tahaseen', '279034', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279035', 'SINGAVARAPU HARSHINI', 'harshini', '279035', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279036', 'TANNEERU MOUNIKA ARCHANA', 'archana', '279036', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279037', 'THOMMANDRU SWATHI', 'swathi', '279037', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279038', 'VALLEPU GIRISH KUMAR', 'girishkumar', '279038', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279039', 'VARUN SANDESH CHINNAM', 'sandeshchinnam', '279039', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279040', 'VATAPALLI GANESH', 'ganesh', '279040', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279041', 'VEERANKI KARTHIK', 'karthik', '279041', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning'), ('Y25AIML279042', 'YASARAPU SWAMY', 'swamy', '279042', 'AIML', '2nd Year', '2025-2029', 'Artificial Intelligence and Machine Learning')]


# =========================================================
# 2ND YEAR CSE REGULAR STUDENTS (Y25)
# =========================================================
cse_2nd_year_data = [
('Y25CSE279001','ABBADASARI PAVITHRA','pavithra','279001','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279002','ADIGARLA MOHAN','mohan','279002','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279003','AVULA VAMSI','vamsi','279003','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279004','BADARLA GANESH','ganesh004','279004','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279005','BADDIPUDI SAMPATH KUMAR','sampath','279005','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279006','BALAGAM KEERTHI','keerthi','279006','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279007','BANDELA AKANKSHA','akanksha','279007','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279008','BATTULA AMAL JASWANTH','amal','279008','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279009','BOGU DURGA LAKSHMI','durgalakshmi','279009','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279010','BOLLEPOGU PRADEEP','pradeep','279010','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279011','BONIGE SUSANTH','susanth','279011','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279012','CHALLA BHARGAVEE DEVI','bhargavee','279012','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279013','CHANDANA NISHITHA DURGA','nishitha','279013','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279014','CHINTALA KARTHIK','karthik014','279014','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279015','CHINTHA SAI','sai','279015','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279016','CHIRUVOLU SRI GIPLIENDRA ROY','gipliendra','279016','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279017','DAKARAPU NEETHUSRI','neethusri','279017','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279018','DASARI ROHAN','rohan','279018','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279019','DEVIREDDY SATYA VENKATA NAGAMANI','nagamani','279019','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279020','DOSAPATI JYOSTHNA','jyosthna','279020','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279021','DUGGEMPUDI VISHNU VARDHAN REDDY','vishnu','279021','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279022','ELAVARAPU SRAVANI','sravani','279022','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279023','ELEPAM KALYANKUMAR','kalyan','279023','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279024','GADI VIJAYA DURGA VARAPRASAD','varaprasad','279024','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279025','GALI VASANTHA KUMAR','vasantha','279025','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279026','GANJALA RAMA LAKSHMI','ramalakshmi','279026','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279027','GARIKIMUKKU UDAY KIRAN KUMAR','uday','279027','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279028','GORJI SWATHI','swathi028','279028','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279029','GUDAVALLI JAGADEESH','jagadeesh','279029','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279030','GUDIPATI DINESH REDDY','dinesh','279030','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279031','GUDIVADA SAI MEGHANA','meghana','279031','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279032','GURINDAPALLI TANUSH','tanush','279032','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279033','JALDULA PHANI KUMAR','phani','279033','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279034','JANYAVULA REETHIKA','reethika','279034','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279035','JUJJAVARAPU MUNNI','munni','279035','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279036','KAKINADA SRIVALLI','srivalli','279036','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279037','KANDRU ANU','anu','279037','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279038','KANDULA MANASA','manasa','279038','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279039','KARRE SANTHOSH KUMAR','santhosh','279039','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279040','LOKARAPU PRUDHVI','prudhvi','279040','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279041','MAHAMMAD ASIF','asif','279041','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279042','MEDURI LEELA NAGA SAI','leela','279042','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279043','MOHAMMAD SHAZIYA BEGUM','shaziya','279043','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279044','MULAPARTHI BANNU','bannu','279044','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279045','MUNTHA EKANTH NAGA SAMBA SIVA CHARI','ekanth','279045','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279046','MYNAM LOKESH','lokesh','279046','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279047','PADAVALA SWATHI PRIYA','swathipriya','279047','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279048','PAGOLU PRANAY VIKYATH','pranay','279048','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279049','PALEPOGU CHANDU','chandu049','279049','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279050','PAPPU SNEHA','sneha','279050','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279051','PARASABATHINA SANTOSH KUMAR','santosh','279051','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279052','PARISE SANTHOSH','santosh052','279052','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279053','PASIKERA YASASWINI USHA SRI','yasaswini','279053','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279054','PEKETI MADHU','madhu','279054','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279055','RONGALI SUHITHA','suhitha','279055','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279056','SHAIK LAL KHAN','lal','279056','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279057','SHAIK RASHEEDHAH','rasheedhah','279057','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279058','SUREDDI SOWJANYA','sowjanya','279058','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279059','TATAKUNTLA RAMYA SRI','ramya','279059','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279060','TIRUMALASETTI KRISHNA SAI','krishnasai','279060','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279061','UPPADA RAMCHARAN TEJA','ramcharan','279061','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279062','UPPULETI VINAY','vinay062','279062','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279063','VANKAYALA BHAVYA','bhavya','279063','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279064','VELIVALA SATHYA SAI KRISHNA','sathya','279064','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279065','VEMULA PAVAN KUMAR','pavan','279065','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('Y25CSE279066','VITTALA NIKITHA','nikitha','279066','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
]

# 2ND YEAR CSE LATERALS (L26)
cse_2nd_lateral_data = [
('L26CSE279001','BANNE MANASA','manasa_l1','279001','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279002','BHIMALA LAKSHMI NAGA DIVYA SUREKHA','divya','279002','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279003','C BHARATH','bharath','279003','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279004','CHANUMURI LOCHANA','lochana','279004','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279005','CHINTHA DRAKSHAYANI','drakshayani','279005','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279006','KONDABATTINA HANUMAN','hanuman','279006','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279007','KORAVANGI KARTHIK','karthik_l7','279007','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279008','KOTTE SAI KIRAN','saikiran','279008','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279009','PERAM ESWAR','eswar','279009','CSE-A','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279010','PILLI PRABHAS','prabhas','279010','CSE-B','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279011','RAJANA DURGA MANGA LAKSHMI','durga','279011','CSE-B','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279012','RAVULAPATI NAGA NARASIMHA SWAMY','narasimha','279012','CSE-B','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279013','SINGAMPALLI RAMESH','ramesh','279013','CSE-B','2nd Year','2025-2029','Computer Science and Engineering'),
('L26CSE279014','VADA SOMESWARA RAO','someswara','279014','CSE-B','2nd Year','2025-2029','Computer Science and Engineering'),
]

# 2ND YEAR AIML LATERALS (L26)
aiml_2nd_lateral_data = [
('L26AIML279001','B. MAHENDRA','mahendra','279001','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279002','C. YOSHINI','yoshini','279002','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279003','C. SUPRIYA','supriya','279003','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279004','D. SURESH KUMAR','suresh','279004','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279005','G. VASU','vasu','279005','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279006','G. ANUSHA','anusha','279006','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279007','J. VENKATESWARA RAO','venkateswara','279007','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279008','K. MADHU TULASI','madhutulasi','279008','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279009','K. VARSHINI CHINNARI','varshini','279009','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279010','K. ANANDA KUMAR','ananda','279010','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279011','K. ANISH','anish','279011','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279012','M. TEJA','teja','279012','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279013','N. SANDESH KUMAR','sandesh','279013','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279014','P. DINESH','dinesh014','279014','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279015','S. MOUNIKA','mounika','279015','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279016','T. ASHOK','ashok016','279016','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279017','T. JAGDESSHCHARAN KUMAR','jagdesshcharan','279017','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
('L26AIML279018','V. KARTHIK','karthik018','279018','AIML','2nd Year','2025-2029','Artificial Intelligence and Machine Learning'),
]



def username_from_name(name, roll_number):
    # Default username uses the student's given name(s), not the surname/initial.
    # Example: "AKURI POOJITHA" -> "poojitha".
    parts = [x for x in (name or "").replace(".", "").split() if x]
    base = "".join(parts[1:]).lower() if len(parts) > 1 else "".join(parts).lower()
    base = "".join(ch for ch in base if ch.isalnum()) or "student"
    return base


def make_unique_student_username(name, roll_number, exclude_id=None):
    """Return a unique username without triggering an unwanted autoflush.

    The bundled seed data contains students whose preferred given-name username
    can collide (for example, two students named Sandeep).  During startup the
    old code changed one student's username and then queried the database;
    SQLAlchemy autoflush could try to write that duplicate before the code had
    a chance to resolve it.
    """
    base = username_from_name(name, roll_number)

    def taken(value):
        query = Student.query.filter_by(username=value)
        if exclude_id is not None:
            query = query.filter(Student.id != exclude_id)
        return query.first() is not None

    with db.session.no_autoflush:
        if not taken(base):
            return base

        suffix = roll_number[-6:] if len(roll_number) >= 6 else roll_number
        username = f"{base}{suffix}"
        counter = 2
        while taken(username):
            username = f"{base}{suffix}{counter}"
            counter += 1
        return username


def student_academic_details(year_name, group_name):
    batches = {
        "1st Year": "2026-2030",
        "2nd Year": "2025-2029",
        "3rd Year": "2024-2028",
        "4th Year": "2023-2027",
    }
    departments = {
        "CSE-A": "Computer Science and Engineering",
        "CSE-B": "Computer Science and Engineering",
        "ECE": "Electronics and Communication Engineering",
        "AIML": "Artificial Intelligence and Machine Learning",
    }
    return batches.get(year_name, ""), departments.get(group_name, "")


def add_student_from_form(actor_role):
    year_name = request.form.get("year", "").strip()
    name = request.form.get("name", "").strip()
    roll_number = request.form.get("roll_number", "").strip().upper()
    group_name = request.form.get("group_name", "").strip().upper()

    valid_years = {"1st Year", "2nd Year", "3rd Year", "4th Year"}
    valid_groups = {"CSE-A", "CSE-B", "ECE", "AIML"}
    if year_name not in valid_years or group_name not in valid_groups or not name or not roll_number:
        return "Year, name, roll number and group are required."

    # Teachers may add students only to one of their assigned groups.
    if actor_role == "teacher":
        teacher = db.session.get(Teacher, session.get("teacher_id"))
        allowed_groups = [g.strip() for g in (teacher.groups or "").split(",") if g.strip()] if teacher else []
        if not teacher or group_name not in allowed_groups:
            return "You are not allowed to add students to this group."

    if Student.query.filter_by(roll_number=roll_number).first():
        return "This roll number already exists."

    batch, department = student_academic_details(year_name, group_name)
    username = make_unique_student_username(name, roll_number)
    password = roll_number[-6:] if len(roll_number) >= 6 else roll_number

    student = Student(
        roll_number=roll_number,
        name=name,
        username=username,
        password=password,
        class_name=group_name,
        year=year_name,
        batch=batch,
        department=department,
        group_name=group_name,
    )
    db.session.add(student)
    actor_name = "Admin"
    if actor_role == "teacher":
        teacher = db.session.get(Teacher, session.get("teacher_id"))
        actor_name = f"Teacher {teacher.name}"
    notify_admin(
        f"{actor_name} added student {name} ({roll_number}) to {year_name} {group_name}. Username: {username}",
        actor_role,
        group_name,
    )
    db.session.commit()
    return None

with app.app_context():

    db.create_all()
    ensure_column("student", "group_name", "VARCHAR(20) NOT NULL DEFAULT 'CSE-A'")
    ensure_column("teacher", "groups", "VARCHAR(100) NOT NULL DEFAULT 'CSE-A,CSE-B,ECE'")
    ensure_column("assignment", "group_name", "VARCHAR(20) NOT NULL DEFAULT 'ALL'")
    ensure_column("notice", "group_name", "VARCHAR(20) NOT NULL DEFAULT 'ALL'")
    ensure_column("pdf", "group_name", "VARCHAR(20) NOT NULL DEFAULT 'ALL'")
    ensure_column("timetable_data", "group_name", "VARCHAR(20) NOT NULL DEFAULT 'ALL'")
    ensure_column("portal_event", "year_name", "VARCHAR(30) NOT NULL DEFAULT 'ALL'")
    db.session.commit()

    # =====================================================
    # ALL 13 TEACHERS
    # =====================================================

    teachers_data = [

        ("SOMU", "somu", "somu@", "CN"),

        ("ABIDA BEGUM", "abida", "abida@", "NIL"),

        ("SALMA BEGUM", "salma", "salma@", "PE-1"),

        ("BHAVANI SHANKAR", "shankar", "shankar@", "NIL"),

        ("PRINCIPAL(QOAD)", "principal", "principal@", "OOAD"),

        ("RAJEEV", "rajeev", "rajeev@", "WCS"),

        ("ALI MIRZA", "ali", "ali@", "DW&DM"),

        ("KAVITHA", "kavitha", "kavitha@", "NIL"),

        ("ROJA", "roja", "roja@", "NIL"),

        ("RANGASREE", "rangasree", "rangasree@", "NIL"),

        ("RANGAV NAIDU", "naidu", "naidu@", "NIL"),

        ("K.G.V.K", "krishna", "krishna@", "NIL"),

        ("BALAJI", "balaji", "balaji@", "NIL")
    ]


    # =====================================================
    # CREATE / UPDATE TEACHERS
    # =====================================================

    for teacher_data in teachers_data:

        name, username, password, subject = teacher_data

        teacher = Teacher.query.filter_by(
            username=username
        ).first()

        if teacher is None:

            teacher = Teacher(
                name=name,
                username=username,
                password=password,
                subject=subject,
                groups="CSE-A,CSE-B,ECE,AIML"
            )

            db.session.add(teacher)

        else:

            teacher.name = name
            teacher.subject = subject
            if not teacher.groups:
                teacher.groups = "CSE-A,CSE-B,ECE,AIML"


    # =====================================================
    # DEFAULT ADMIN
    # =====================================================

    admin = Admin.query.filter_by(
        username="faruk"
    ).first()

    if admin is None:

        admin = Admin(
            username="faruk",
            password="admin"
        )

        db.session.add(admin)


    # =====================================================
    # CREATE / UPDATE STUDENTS
    # =====================================================

    for student_data in students_data:

        if len(student_data) != 5:

            print("ERROR: Invalid student data:")
            print(student_data)

            continue

        roll_number, name, username, password, class_name = student_data

        student = Student.query.filter_by(
            roll_number=roll_number
        ).first()

        if student is None:

            student = Student(
                roll_number=roll_number,
                name=name,
                username=username,
                password=password,
                class_name=class_name,
                year="3rd Year",
                batch="2024-2028",
                department="Computer Science and Engineering"
            )

            db.session.add(student)

        

        else:
            student.name = name
            student.class_name = class_name
            student.year = "3rd Year"
            student.batch = "2024-2028"
            student.department = "Computer Science and Engineering"

    # =====================================================
    # ADD LATERAL + ECE STUDENTS
    # =====================================================

    for row in additional_students_data:
        roll_number, name, username, password, group_name, year, batch, department = row
        student = Student.query.filter_by(roll_number=roll_number).first()
        username = make_unique_student_username(name, roll_number, student.id if student else None)
        if student is None:
            student = Student(roll_number=roll_number, name=name, username=username, password=password,
                              class_name=group_name, year=year, batch=batch, department=department,
                              group_name=group_name)
            db.session.add(student)
        else:
            student.name = name
            student.username = make_unique_student_username(name, roll_number, student.id)
            student.password = password
            student.class_name = group_name
            student.year = year
            student.batch = batch
            student.department = department
            student.group_name = group_name

    # 2nd Year AIML students: Y25AIML279001-Y25AIML279042.
    # Username is based on the student's given name (last name token), not surname.
    for row in aiml_2nd_year_data:
        roll_number, name, username, password, group_name, year, batch, department = row
        username = username_from_name(name, roll_number)
        student = Student.query.filter_by(roll_number=roll_number).first()
        username = make_unique_student_username(name, roll_number, student.id if student else None)
        if student is None:
            student = Student(roll_number=roll_number, name=name, username=username, password=password,
                              class_name=group_name, year=year, batch=batch, department=department,
                              group_name=group_name)
            db.session.add(student)
        else:
            student.name = name
            student.username = make_unique_student_username(name, roll_number, student.id)
            student.password = password
            student.class_name = group_name
            student.year = year
            student.batch = batch
            student.department = department
            student.group_name = group_name

    # Add/update all newly supplied 2nd-year regular and lateral students.
    for row in cse_2nd_year_data + cse_2nd_lateral_data + aiml_2nd_lateral_data + aiml_2nd_year_data:
        roll_number, name, username, password, group_name, year, batch, department = row
        username = username_from_name(name, roll_number)
        student = Student.query.filter_by(roll_number=roll_number).first()
        username = make_unique_student_username(name, roll_number, student.id if student else None)
        if student is None:
            student = Student(roll_number=roll_number, name=name, username=username, password=password,
                              class_name=group_name, year=year, batch=batch, department=department, group_name=group_name)
            db.session.add(student)
        else:
            student.name = name
            student.username = make_unique_student_username(name, roll_number, student.id)
            student.password = password
            student.class_name = group_name
            student.year = year
            student.batch = batch
            student.department = department
            student.group_name = group_name

    # Canonical academic year/branch mapping from roll-number format.
    # Y24 = 3rd year regular; L25 = 3rd year lateral.
    # Y25 = 2nd year regular; L26 = 2nd year lateral.
    for student in Student.query.all():
        roll = (student.roll_number or "").upper()
        if roll.startswith("Y24"):
            student.year = "3rd Year"
            student.batch = "2024-2028"
        elif roll.startswith("L25"):
            student.year = "3rd Year"
            student.batch = "2025-2027"
        elif roll.startswith("Y25"):
            student.year = "2nd Year"
            student.batch = "2025-2029"
        elif roll.startswith("L26"):
            student.year = "2nd Year"
            student.batch = "2025-2029"

        if "CSE" in roll:
            student.department = "Computer Science and Engineering"
            if student.class_name in ("CSE-A", "CSE-B"):
                student.group_name = student.class_name
            elif not student.group_name:
                student.group_name = "CSE-A"
        elif "AIML" in roll:
            student.department = "Artificial Intelligence and Machine Learning"
            student.group_name = "AIML"
        elif "ECE" in roll:
            student.department = "Electronics and Communication Engineering"
            student.group_name = "ECE"

    # Existing content remains visible to all groups until newly targeted content is created.
    # This is done by migration below.

    # Legacy timetable is CSE-wide; it is not shown to ECE.
    for timetable_row in TimetableData.query.filter_by(group_name="ALL").all():
        timetable_row.group_name = "CSE"

    # =====================================================
    # SAVE DATABASE
    # =====================================================

    db.session.commit()

    print("====================================")
    print("DATABASE INITIALIZED SUCCESSFULLY")
    print("13 TEACHERS ADDED / UPDATED")
    print("STUDENTS ADDED / UPDATED")
    print("ADMIN READY")
    print("====================================")


# =========================================================
# DATE FORMAT HELPER
# =========================================================

def format_date(date_value):

    if not date_value:
        return ""

    date_value = str(date_value).strip()

    # Already DD-MM-YYYY
    try:

        if (
            len(date_value) == 10
            and date_value[2] == "-"
            and date_value[5] == "-"
        ):

            datetime.strptime(
                date_value,
                "%d-%m-%Y"
            )

            return date_value

    except ValueError:
        pass


    # YYYY-MM-DD
    try:

        converted = datetime.strptime(
            date_value,
            "%Y-%m-%d"
        )

        return converted.strftime(
            "%d-%m-%Y"
        )

    except ValueError:

        return date_value


# =========================================================
# JINJA DATE FILTER
# =========================================================

@app.template_filter("date_format")
def date_format_filter(value):

    return format_date(value)


@app.context_processor
def inject_portal_event_state():
    try:
        latest = db.session.query(db.func.max(PortalEvent.id)).scalar() or 0
    except Exception:
        latest = 0
    return {"portal_latest_event_id": latest}


# =========================================================
# MAIN LOGIN
# =========================================================

@app.route("/")
def login():

    return render_template(
        "login.html"
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def do_login():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()

    selected_year = request.form.get("year", "").strip()
    selected_group = request.form.get("group_name", "").strip().upper()
    if selected_year not in ("1st Year", "2nd Year", "3rd Year", "4th Year"):
        return "Please select your year."
    if selected_group not in ("CSE-A", "CSE-B", "ECE", "AIML"):
        return "Please select a valid group."

    student = Student.query.filter_by(
        username=username
    ).first()

    if student is None:

        return "Username not found"

    if student.password != password:

        return "Password is incorrect"

    if student.year != selected_year:
        return "The selected year does not match this student account."

    if student.group_name != selected_group:
        return "The selected group does not match this student account."

    session.clear()

    session["student_id"] = student.id
    session["group_name"] = selected_group
    session["year_name"] = selected_year

    return redirect("/dashboard")


# =========================================================
# TEACHER LOGIN PAGE
# =========================================================

@app.route("/teacher-login")
def teacher_login():

    return render_template(
        "teacher_login.html"
    )


# =========================================================
# TEACHER LOGIN PROCESS
# =========================================================

@app.route("/teacher-login", methods=["POST"])
def do_teacher_login():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()

    selected_year = request.form.get("year", "").strip()
    selected_group = request.form.get("group_name", "").strip().upper()
    if selected_year not in ("1st Year", "2nd Year", "3rd Year", "4th Year"):
        return "Please select your year."
    if selected_group not in ("CSE-A", "CSE-B", "ECE", "AIML"):
        return "Please select a valid group."

    teacher = Teacher.query.filter_by(
        username=username
    ).first()

    if teacher and teacher.password == password:

        allowed_groups = [g.strip().upper() for g in (teacher.groups or "CSE-A,CSE-B,ECE,AIML").split(",")]
        if selected_group not in allowed_groups:
            return "This teacher is not assigned to the selected group."

        session.clear()

        session["teacher_id"] = teacher.id
        session["group_name"] = selected_group
        session["year_name"] = selected_year

        return redirect(
            "/teacher-dashboard"
        )

    return "Invalid teacher username or password"


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login")
def admin_login():

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN LOGIN PROCESS
# =========================================================

@app.route("/admin-login", methods=["POST"])
def do_admin_login():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()

    admin = Admin.query.filter_by(
        username=username
    ).first()

    if admin and admin.password == password:

        session.clear()

        session["admin_id"] = admin.id

        return redirect(
            "/admin-dashboard"
        )

    return "Invalid admin username or password"




def current_group():
    return session.get("group_name") or "CSE-A"

def current_year():
    return session.get("year_name") or "3rd Year"

def group_filter(query, model):
    group = current_group()
    if hasattr(model, "group_name"):
        return query.filter(model.group_name.in_([group, "ALL"]))
    return query

# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    student_id = session.get(
        "student_id"
    )

    if not student_id:

        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:

        session.clear()

        return redirect("/")

    return render_template(
        "dashboard.html",
        student=student
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return redirect(
            "/teacher-login"
        )

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:

        session.clear()

        return redirect(
            "/teacher-login"
        )

    students = Student.query.filter(Student.group_name == current_group(), Student.year == current_year()).order_by(Student.roll_number).all()

    return render_template(
        "teacher_dashboard.html",
        teacher=teacher,
        students=students
    )


# =========================================================
# TEACHER ATTENDANCE
# =========================================================

@app.route(
    "/teacher-attendance",
    methods=["GET", "POST"]
)
def teacher_attendance():

    teacher_id = session.get(
        "teacher_id"
    )

    if not teacher_id:

        return redirect(
            "/teacher-login"
        )

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:

        session.clear()

        return redirect(
            "/teacher-login"
        )


    # =====================================================
    # SAVE ATTENDANCE
    # =====================================================

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        selected_date = request.form.get(
            "attendance_date",
            ""
        ).strip()

        if not subject:

            return "Please enter a subject."

        if not selected_date:

            return "Please select a date."


        # -------------------------------------------------
        # Convert HTML date YYYY-MM-DD
        # to DD-MM-YYYY
        # -------------------------------------------------

        try:

            selected_date_object = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            )

            attendance_date = selected_date_object.strftime(
                "%d-%m-%Y"
            )

        except ValueError:

            return "Invalid date format."


        students = Student.query.filter(Student.group_name == current_group(), Student.year == current_year()).order_by(Student.roll_number).all()


        # -------------------------------------------------
        # SAVE EACH STUDENT
        # -------------------------------------------------

        for student in students:

            attendance_value = request.form.get(
                f"attendance_{student.id}"
            )

            if attendance_value == "present":

                status = "Present"

            else:

                status = "Absent"


            # -------------------------------------------------
            # CHECK EXISTING RECORD
            # -------------------------------------------------

            record = Attendance.query.filter_by(
                student_id=student.id,
                subject=subject,
                attendance_date=attendance_date
            ).first()


            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------

            if record is None:

                record = Attendance(
                    student_id=student.id,
                    subject=subject,
                    attendance_date=attendance_date,
                    status=status,
                    teacher_id=teacher.id
                )

                db.session.add(record)


            # -------------------------------------------------
            # UPDATE
            # -------------------------------------------------

            else:

                record.status = status
                record.teacher_id = teacher.id


        notify_portals(f"{teacher.name} updated attendance for {current_group()} — {subject}", "teacher", current_group(), "update")
        db.session.commit()


        print(
            "===================================="
        )

        print(
            "ATTENDANCE SAVED SUCCESSFULLY"
        )

        print(
            "Teacher:",
            teacher.name
        )

        print(
            "Subject:",
            subject
        )

        print(
            "Date:",
            attendance_date
        )

        print(
            "===================================="
        )


        return redirect(
            "/teacher-attendance"
        )


    # =====================================================
    # SHOW ATTENDANCE HISTORY
    # =====================================================

    students = Student.query.filter(Student.group_name == current_group(), Student.year == current_year()).order_by(Student.roll_number).all()

    attendance_history = Attendance.query.join(Student).filter(Student.group_name == current_group(), Student.year == current_year()).order_by(Attendance.id.desc()).all()

    return render_template(
        "teacher_attendance.html",
        teacher=teacher,
        students=students,
        attendance_history=attendance_history
    )

# =========================================================
# TEACHER TIMETABLE
# =========================================================

@app.route("/teacher-timetable")
def teacher_timetable():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    timetable = TimetableData.query.filter(TimetableData.group_name.in_([current_group(), "CSE", "ALL"])).order_by(TimetableData.id.desc()).first()

    if timetable is None:
        timetable = TimetableData(
            monday="PE-I|OOAD|WCS|CN|DWD&DM|📖 Library",
            tuesday="CN|DWD&DM|PE-I|🧪 Flutter Lab / SOC-III",
            wednesday="DWD&DM|CN|OOAD|WCS|PE-I|⚽ Sports",
            thursday="🧪 SOC-III / Flutter Lab|CN|OOAD|📖 Library",
            friday="PE-I|WCS|OOAD|🧪 CN LAB / DWD&DM LAB",
            saturday="🧪 DWD&DM LAB / CN LAB|DWD&DM|WCS|⚽ Sports",
            group_name=current_group()
        )

        db.session.add(timetable)
        db.session.commit()

    return render_template(
        "teacher_timetable.html",
        timetable=timetable
    )
# =========================================================
# EDIT TEACHER TIMETABLE
# =========================================================

@app.route("/teacher-timetable-edit", methods=["GET", "POST"])
def teacher_timetable_edit():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    timetable = TimetableData.query.filter(TimetableData.group_name.in_([current_group(), "CSE", "ALL"])).order_by(TimetableData.id.desc()).first()

    if timetable is None:
        return redirect("/teacher-timetable")

    if request.method == "POST":

        timetable.monday = "|".join(request.form.getlist("monday"))
        timetable.tuesday = "|".join(request.form.getlist("tuesday"))
        timetable.wednesday = "|".join(request.form.getlist("wednesday"))
        timetable.thursday = "|".join(request.form.getlist("thursday"))
        timetable.friday = "|".join(request.form.getlist("friday"))
        timetable.saturday = "|".join(request.form.getlist("saturday"))
        timetable.group_name = current_group()
        notify_admin(f"{teacher.name} updated timetable for {current_group()}", "teacher", current_group())

        db.session.commit()

        return redirect("/teacher-timetable")

    return render_template(
        "teacher_timetable_edit.html",
        timetable=timetable
    )
# =========================================================
# TEACHER NOTICES
# =========================================================

@app.route("/teacher-notices")
def teacher_notices():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    notices = group_filter(Notice.query.order_by(Notice.id.desc()), Notice).all()

    return render_template(
        "teacher_notices.html",
        teacher=teacher,
        notices=notices
    )
# =========================================================
# TEACHER ASSIGNMENTS
# =========================================================

@app.route("/teacher-assignments", methods=["GET", "POST"])
def teacher_assignments():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    # =====================================================
    # ADD ASSIGNMENT
    # =====================================================

    if request.method == "POST":

        subject = request.form.get("subject", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "").strip()

        if not subject or not title or not description or not due_date:
            return "All assignment fields are required."

        assignment = Assignment(
            title=title,
            subject=subject,
            description=description,
            due_date=due_date,
            teacher_id=teacher_id,
            group_name=current_group()
        )

        db.session.add(assignment)
        notify_admin(f"{teacher.name} added an assignment for {current_group()}: {title}", "teacher", current_group())
        db.session.commit()

        # =================================================
        # UPLOAD PICTURE / PDF
        # =================================================

        uploaded_file = request.files.get("attachment")

        if uploaded_file and uploaded_file.filename:

            original_filename = uploaded_file.filename

            allowed_extensions = {
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "webp"
            }

            extension = (
                original_filename
                .rsplit(".", 1)[-1]
                .lower()
            )

            if extension not in allowed_extensions:
                return (
                    "Only PDF, JPG, JPEG, PNG and WEBP "
                    "files are allowed."
                )

            safe_name = secure_filename(
                original_filename
            )

            unique_filename = (
                str(int(time.time()))
                + "_"
                + safe_name
            )

            uploaded_file.save(
                os.path.join(
                    ASSIGNMENT_UPLOAD_FOLDER,
                    unique_filename
                )
            )

            attachment = AssignmentAttachment(
                assignment_id=assignment.id,
                filename=unique_filename,
                original_filename=original_filename
            )

            db.session.add(attachment)
            db.session.commit()

        return redirect("/teacher-assignments")

    # =====================================================
    # SHOW ASSIGNMENTS
    # =====================================================

    assignments = group_filter(Assignment.query.order_by(Assignment.id.desc()), Assignment).all()

    return render_template(
        "teacher_assignments.html",
        teacher=teacher,
        assignments=assignments
    )
@app.route("/assignment-file/<filename>")
def assignment_file(filename):

    student_id = session.get("student_id")
    teacher_id = session.get("teacher_id")

    if not student_id and not teacher_id:
        return redirect("/")

    return send_from_directory(
        ASSIGNMENT_UPLOAD_FOLDER,
        filename
    )
# =========================================================
# DELETE ASSIGNMENT
# =========================================================

@app.route(
    "/delete-assignment/<int:assignment_id>",
    methods=["POST"]
)
def delete_assignment(assignment_id):

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    assignment = db.session.get(
        Assignment,
        assignment_id
    )

    if assignment is None:
        return redirect("/teacher-assignments")

    # Only the teacher who created it can delete it
    if assignment.teacher_id != teacher_id:
        return redirect("/teacher-assignments")

    db.session.delete(assignment)
    db.session.commit()

    return redirect("/teacher-assignments")
# =========================================================
# ASSIGNMENT ATTACHMENT TABLE
# =========================================================

class AssignmentAttachment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("assignment.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(300),
        nullable=False
    )

    original_filename = db.Column(
        db.String(300),
        nullable=False
    )

    assignment = db.relationship(
        "Assignment",
        backref="attachments"
    )
# =========================================================
# ADD NOTICE
# =========================================================

@app.route("/add-notice", methods=["POST"])
def add_notice():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    title = request.form.get("title", "").strip()
    message = request.form.get("message", "").strip()
    notice_date = request.form.get("notice_date", "").strip()

    if not title:
        return "Notice title is required."

    if not message:
        return "Notice message is required."

    if not notice_date:
        notice_date = date.today().strftime("%d-%m-%Y")
    else:
        try:
            notice_date = datetime.strptime(
                notice_date,
                "%Y-%m-%d"
            ).strftime("%d-%m-%Y")
        except ValueError:
            pass

    # CREATE NOTICE
    notice = Notice(
        title=title,
        message=message,
        notice_date=notice_date,
        teacher_id=teacher_id,
        group_name=current_group()
    )

    db.session.add(notice)
    notify_admin(f"{teacher.name} posted a notice for {current_group()}: {title}", "teacher", current_group())
    db.session.commit()

    # UPLOAD IMAGE / PDF
    uploaded_file = request.files.get("attachment")

    if uploaded_file and uploaded_file.filename:

        original_filename = secure_filename(
            uploaded_file.filename
        )

        extension = os.path.splitext(
            original_filename
        )[1].lower()

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf"
        ]

        if extension in allowed_extensions:

            unique_filename = (
                str(int(time.time() * 1000))
                + "_"
                + original_filename
            )

            file_path = os.path.join(
                NOTICE_UPLOAD_FOLDER,
                unique_filename
            )

            uploaded_file.save(file_path)

            if extension == ".pdf":
                file_type = "pdf"
            else:
                file_type = "image"

            attachment = NoticeAttachment(
                notice_id=notice.id,
                filename=unique_filename,
                original_filename=original_filename,
                file_type=file_type
            )

            db.session.add(attachment)
            db.session.commit()

    return redirect("/teacher-notices")
# =========================================================
# DELETE NOTICE
# =========================================================

@app.route("/delete-notice/<int:notice_id>", methods=["POST"])
def delete_notice(notice_id):

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    notice = db.session.get(Notice, notice_id)

    if notice is None:
        return redirect("/teacher-notices")

    # Delete attached files from the folder
    for attachment in notice.attachments:

        file_path = os.path.join(
            NOTICE_UPLOAD_FOLDER,
            attachment.filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(attachment)

    # Delete notice
    db.session.delete(notice)
    db.session.commit()

    return redirect("/teacher-notices")

# =========================================================
# NOTICE ATTACHMENT
# =========================================================

@app.route("/notice-file/<path:filename>")
def notice_file(filename):

    return send_from_directory(
        NOTICE_UPLOAD_FOLDER,
        filename,
        as_attachment=False
    )
@app.route("/student-account", methods=["GET", "POST"])
def student_account():
    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(Student, student_id)

    if student is None:
        session.clear()
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "Username and password cannot be empty."

        # Check whether another student already has this username
        existing_student = Student.query.filter(
            Student.username == username,
            Student.id != student.id
        ).first()

        if existing_student:
            return "This username is already used by another student."

        student.username = username
        student.password = password

        db.session.commit()

        return redirect("/student-account")

    return render_template("student_account.html", student=student)

# =========================================================
# STUDENT ATTENDANCE
# =========================================================

@app.route("/attendance")
def attendance():

    student_id = session.get(
        "student_id"
    )

    if not student_id:

        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:

        session.clear()

        return redirect("/")


    attendance_records = Attendance.query.filter_by(
        student_id=student.id
    ).all()

    # Attendance dates in the database may be stored in different formats
    # (for example 2026-08-28 or 28-08-2026). Normalize them for sorting
    # and display them as DD/MM/YY. Newest month/date appears first.
    from datetime import datetime as _attendance_datetime

    def _attendance_date_value(record):
        raw = record.attendance_date
        if hasattr(raw, "strftime"):
            return raw
        raw = str(raw).strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return _attendance_datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return _attendance_datetime.min

    attendance_records.sort(key=_attendance_date_value, reverse=True)

    # Add a presentation-only formatted date and month label.
    current_month = None
    for record in attendance_records:
        parsed_date = _attendance_date_value(record)
        record.display_date = (
            parsed_date.strftime("%d/%m/%y")
            if parsed_date != _attendance_datetime.min
            else str(record.attendance_date)
        )
        record.display_month = (
            parsed_date.strftime("%B %Y")
            if parsed_date != _attendance_datetime.min
            else "Other"
        )


    # -----------------------------------------------------
    # SUBJECT-WISE CALCULATION
    # -----------------------------------------------------

    subjects = {}


    for record in attendance_records:

        if record.subject not in subjects:

            subjects[record.subject] = {
                "attended": 0,
                "total": 0,
                "percentage": 0
            }


        subjects[
            record.subject
        ]["total"] += 1


        if record.status == "Present":

            subjects[
                record.subject
            ]["attended"] += 1


    # -----------------------------------------------------
    # CALCULATE PERCENTAGE
    # -----------------------------------------------------

    for subject_name in subjects:

        attended = subjects[
            subject_name
        ]["attended"]

        total = subjects[
            subject_name
        ]["total"]


        if total > 0:

            subjects[
                subject_name
            ]["percentage"] = round(
                (attended / total) * 100,
                2
            )

        else:

            subjects[
                subject_name
            ]["percentage"] = 0


    return render_template(
        "attendance.html",
        student=student,
        attendance_records=attendance_records,
        subjects=subjects
    )


# =========================================================
# STUDENT TIMETABLE
# =========================================================

@app.route("/timetable")
def timetable():

    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(Student, student_id)

    if student is None:
        session.clear()
        return redirect("/")

    # Get timetable from database
    timetable = TimetableData.query.filter(TimetableData.group_name.in_([current_group(), "CSE", "ALL"])).order_by(TimetableData.id.desc()).first()

    if timetable is None:
        return "Timetable is not available."

    return render_template(
        "timetable.html",
        student=student,
        timetable=timetable
    )


# =========================================================
# MARKS
# =========================================================

@app.route("/marks")
def marks():

    student_id = session.get(
        "student_id"
    )

    if not student_id:

        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:

        session.clear()

        return redirect("/")


    marks_records = Marks.query.filter_by(
        student_id=student.id
    ).all()


    return render_template(
        "marks.html",
        student=student,
        marks_records=marks_records
    )
# =========================================================
# STUDENT ASSIGNMENTS
# =========================================================

@app.route("/assignments")
def student_assignments():

    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:
        session.clear()
        return redirect("/")

    assignments = group_filter(Assignment.query.order_by(Assignment.id.desc()), Assignment).all()

    return render_template(
        "assignments.html",
        student=student,
        assignments=assignments
    )
# =========================================================
# STUDENT NOTICES
# =========================================================
@app.route("/notices")
def notices():
    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(Student, student_id)

    if student is None:
        session.clear()
        return redirect("/")

    notices = group_filter(Notice.query.order_by(Notice.id.desc()), Notice).all()

    return render_template(
        "notices.html",
        student=student,
        notices=notices
    )

# =========================================================
# RESULTS
# =========================================================

@app.route("/results")
def results():

    student_id = session.get(
        "student_id"
    )

    if not student_id:

        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:

        session.clear()

        return redirect("/")

    marks_records = Marks.query.filter_by(
        student_id=student.id
    ).order_by(Marks.subject).all()

    return render_template(
        "results.html",
        student=student,
        marks_records=marks_records
    )
# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# TEACHER LOGOUT
# =========================================================
@app.route("/teacher-logout")
def teacher_logout():

    session.clear()

    return redirect("/teacher-login")
# =========================================================
# TEACHER ACCOUNT SETTINGS
# =========================================================

@app.route("/teacher-account", methods=["GET", "POST"])
def teacher_account():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "Username and password cannot be empty."

        existing_teacher = Teacher.query.filter(
            Teacher.username == username,
            Teacher.id != teacher.id
        ).first()

        if existing_teacher:
            return "This username is already used by another teacher."

        teacher.username = username
        teacher.password = password

        db.session.commit()

        return redirect("/teacher-account")

    return render_template(
        "teacher_account.html",
        teacher=teacher
    )


# =========================================================
# TEACHER MANAGE PDFs
# =========================================================

@app.route("/manage-pdfs")
def manage_pdfs():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:

        session.clear()

        return redirect("/teacher-login")

    pdfs = PDF.query.order_by(
        PDF.id.desc()
    ).all()

    return render_template(
        "manage_pdfs.html",
        teacher=teacher,
        pdfs=pdfs
    )

# =========================================================
# UPLOAD PDF
# =========================================================

@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(
        Teacher,
        teacher_id
    )

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    uploaded_file = request.files.get("pdf_file")

    title = request.form.get(
        "title",
        "Study Material"
    ).strip()

    if uploaded_file is None:
        return "Please select a PDF file."

    if uploaded_file.filename == "":
        return "Please select a PDF file."

    original_filename = uploaded_file.filename

    safe_filename = secure_filename(
        original_filename
    )

    if not safe_filename.lower().endswith(".pdf"):
        return "Only PDF files are allowed."

    unique_filename = (
        str(int(time.time()))
        + "_"
        + safe_filename
    )

    file_path = os.path.join(
        app.config["PDF_FOLDER"],
        unique_filename
    )

    uploaded_file.save(file_path)

    pdf = PDF(
        filename=unique_filename,
        original_filename=original_filename,
        title=title if title else "Study Material",
        uploaded_by=teacher.id,
        upload_date=datetime.now().strftime("%d-%m-%Y"),
        group_name=current_group()
    )

    db.session.add(pdf)
    notify_admin(f"{teacher.name} uploaded study material for {current_group()}: {title}", "teacher", current_group())

    db.session.commit()

    return redirect("/manage-pdfs")


# =========================================================
# STUDENT STUDY MATERIALS / PDF PAGE
# =========================================================
@app.route("/study-materials")
def study_materials():
    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(Student, student_id)

    if student is None:
        session.clear()
        return redirect("/")

    pdfs = group_filter(PDF.query.order_by(PDF.id.desc()), PDF).all()

    return render_template(
        "study_materials.html",
        student=student,
        pdfs=pdfs
    )

# =========================================================
# OPEN PDF IN BROWSER
# =========================================================

@app.route("/pdf/<filename>")
def open_pdf(filename):

    return send_from_directory(
        app.config["PDF_FOLDER"],
        filename
    )


# =========================================================
# DELETE PDF
# =========================================================

@app.route("/delete-pdf/<int:pdf_id>", methods=["POST"])
def delete_pdf(pdf_id):

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    pdf = db.session.get(
        PDF,
        pdf_id
    )

    if pdf is None:
        return "PDF not found."

    file_path = os.path.join(
        app.config["PDF_FOLDER"],
        pdf.filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(pdf)

    db.session.commit()

    return redirect("/manage-pdfs")




@app.route("/teacher-save-result", methods=["POST"])
def teacher_save_result():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect("/teacher-login")
    teacher = db.session.get(Teacher, teacher_id)
    if teacher is None:
        session.clear(); return redirect("/teacher-login")
    student_id = request.form.get("student_id", type=int)
    mark_id = request.form.get("mark_id", type=int)
    subject = request.form.get("subject", "").strip()
    internal = request.form.get("internal", type=int)
    external = request.form.get("external", type=int)
    student = db.session.get(Student, student_id)
    if not student or student.group_name != current_group():
        return "Student is not in the selected group."
    if not subject or internal is None or external is None:
        return "All marks fields are required."
    if mark_id:
        mark = db.session.get(Marks, mark_id)
        if not mark or mark.student_id != student.id:
            return "Mark record not found."
        mark.subject, mark.internal, mark.external = subject, internal, external
        action = "updated"
    else:
        mark = Marks(student_id=student.id, subject=subject, internal=internal, external=external)
        db.session.add(mark)
        action = "added"
    notify_admin(f"{teacher.name} {action} marks for {student.name} ({student.roll_number}) in {current_group()}: {subject}", "teacher", current_group())
    db.session.commit()
    return redirect("/teacher-marks")


@app.route("/teacher-marks")
def teacher_marks():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    students = Student.query.filter(Student.group_name == current_group(), Student.year == current_year()).order_by(Student.roll_number).all()

    return render_template(
        "teacher_marks.html",
        teacher=teacher,
        students=students
    )


@app.route("/teacher-results")
def teacher_results():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    teacher = db.session.get(Teacher, teacher_id)

    if teacher is None:
        session.clear()
        return redirect("/teacher-login")

    marks_records = Marks.query.join(Student).filter(Student.group_name == current_group()).order_by(
        Student.roll_number, Marks.subject
    ).all()

    return render_template(
        "teacher_results.html",
        teacher=teacher,
        marks_records=marks_records
    )


# Backward-compatible route for older links
@app.route("/teacher-results-edit")
def teacher_results_edit_legacy():
    return redirect("/teacher-marks")


# =========================================================
# CHAT BOARDS
# =========================================================
def all_chat_groups():
    # Chat boards available in the current college data.
    # 3rd Year has no AIML branch, and 4th Year data has not been added yet.
    return [
        ("1st Year", "CSE-A"), ("1st Year", "CSE-B"), ("1st Year", "ECE"), ("1st Year", "AIML"),
        ("2nd Year", "CSE-A"), ("2nd Year", "CSE-B"), ("2nd Year", "ECE"), ("2nd Year", "AIML"),
        ("3rd Year", "CSE-A"), ("3rd Year", "CSE-B"), ("3rd Year", "ECE")
    ]

def student_board_names(year, group):
    label = f"{year} {group}"
    return [f"{label} — Students Only", f"{label} — Students + Teachers"]

def teacher_board_names():
    return [f"{year} {group} — Students + Teachers" for year, group in all_chat_groups()]

def teacher_board_name(year, group):
    return f"{year} {group} — Students + Teachers"

def get_chat_identity():
    if session.get("student_id"):
        user = db.session.get(Student, session["student_id"])
        if user:
            return "student", user.id, user.name, user.group_name, user.year
    if session.get("teacher_id"):
        user = db.session.get(Teacher, session["teacher_id"])
        if user:
            return "teacher", user.id, user.name, current_group(), current_year()
    if session.get("admin_id"):
        user = db.session.get(Admin, session["admin_id"])
        if user:
            return "admin", user.id, user.username, "ALL", None
    return None

@app.route("/chat")
def chat():
    identity = get_chat_identity()
    if not identity:
        return redirect("/")
    role, user_id, user_name, group, year = identity
    if role == "student":
        boards = student_board_names(year, group)
    elif role == "teacher":
        boards = teacher_board_names()
    else:
        boards = [f"{y} {g} — Students Only" for y, g in all_chat_groups()] + [f"{y} {g} — Students + Teachers" for y, g in all_chat_groups()]
    selected = request.args.get("board", "").strip()
    if selected not in boards:
        selected = boards[0]
    messages = ChatMessage.query.filter_by(board_name=selected).order_by(ChatMessage.id.asc()).all()
    return render_template("chat.html", boards=boards, selected_board=selected, messages=messages, identity=identity)

@app.route("/chat/send", methods=["POST"])
def chat_send():
    identity = get_chat_identity()
    if not identity:
        return redirect("/")
    role, user_id, user_name, group, year = identity
    board = request.form.get("board_name", "").strip()
    message = request.form.get("message", "").strip()
    uploaded = request.files.get("attachment")
    allowed = student_board_names(year, group) if role == "student" else (teacher_board_names() if role == "teacher" else [f"{y} {g} — Students Only" for y, g in all_chat_groups()] + [f"{y} {g} — Students + Teachers" for y, g in all_chat_groups()])
    if board not in allowed:
        return "You are not allowed to use this chat board.", 403
    if not message and (not uploaded or not uploaded.filename):
        return "Type a message or choose a file."
    filename = original = None
    if uploaded and uploaded.filename:
        original = uploaded.filename
        filename = f"{int(time.time()*1000)}_{secure_filename(original)}"
        uploaded.save(os.path.join(app.config["CHAT_UPLOAD_FOLDER"], filename))
    db.session.add(ChatMessage(board_name=board, sender_role=role, sender_id=user_id, sender_name=user_name, message=message or None, attachment_name=filename, attachment_original_name=original))
    notify_portals(f"New chat message in {board} from {user_name}", role, group, "chat")
    db.session.commit()
    return redirect("/chat?board=" + quote(board))

@app.route("/chat-messages")
def chat_messages_api():
    identity = get_chat_identity()
    if not identity:
        return {"messages": []}
    role, user_id, user_name, group, year = identity
    board = request.args.get("board", "").strip()
    allowed = student_board_names(year, group) if role == "student" else (teacher_board_names() if role == "teacher" else [f"{y} {g} — Students Only" for y, g in all_chat_groups()] + [f"{y} {g} — Students + Teachers" for y, g in all_chat_groups()])
    if board not in allowed:
        return {"messages": []}, 403
    try:
        after = int(request.args.get("after", "0"))
    except ValueError:
        after = 0
    rows = ChatMessage.query.filter(ChatMessage.board_name == board, ChatMessage.id > after).order_by(ChatMessage.id.asc()).limit(50).all()
    return {"messages": [{"id":m.id,"sender_name":m.sender_name,"sender_role":m.sender_role,"sender_id":m.sender_id,"message":m.message or "","attachment_name":m.attachment_name or "","attachment_original_name":m.attachment_original_name or "","created_at":m.created_at.strftime("%d/%m/%Y %H:%M")} for m in rows]}

@app.route("/chat-file/<path:filename>")
def chat_file(filename):
    identity = get_chat_identity()
    if not identity:
        return redirect("/")
    return send_from_directory(app.config["CHAT_UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/portal-events")
def portal_events():
    identity = get_chat_identity()
    if not identity:
        return {"events": [], "latest_id": 0}
    role, user_id, user_name, group, year = identity
    try:
        after = int(request.args.get("after", "0"))
    except ValueError:
        after = 0
    q = PortalEvent.query.filter(PortalEvent.id > after)
    if role != "admin":
        q = q.filter(PortalEvent.group_name.in_([group, "ALL"]), PortalEvent.year_name.in_([year, "ALL"]))
    events = q.order_by(PortalEvent.id.asc()).limit(20).all()
    return {"events": [{"id":e.id,"message":e.message,"type":e.event_type,"created_at":e.created_at.strftime("%d/%m/%Y %H:%M")} for e in events], "latest_id": (events[-1].id if events else after)}


@app.route("/admin-notifications")
def admin_notifications():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    notifications = Notification.query.order_by(Notification.id.desc()).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return render_template("admin_notifications.html", notifications=notifications)


@app.route("/admin-dashboard")
def admin_dashboard():

    admin_id = session.get("admin_id")

    if not admin_id:
        return redirect("/admin-login")

    admin = db.session.get(
        Admin,
        admin_id
    )

    if admin is None:
        session.clear()
        return redirect("/admin-login")

    students_count = Student.query.count()

    teachers_count = Teacher.query.count()

    pdfs_count = PDF.query.count()

    attendance_count = Attendance.query.count()

    marks_count = Marks.query.count()
    notifications_count = Notification.query.filter_by(is_read=False).count()

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        students_count=students_count,
        teachers_count=teachers_count,
        pdfs_count=pdfs_count,
        attendance_count=attendance_count,
        marks_count=marks_count,
        notifications_count=notifications_count
    )
@app.route("/admin-add-student", methods=["POST"])
def admin_add_student():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    error = add_student_from_form("admin")
    if error:
        return error
    return redirect("/admin-students")


@app.route("/teacher-add-student", methods=["POST"])
def teacher_add_student():
    if not session.get("teacher_id"):
        return redirect("/teacher-login")
    error = add_student_from_form("teacher")
    if error:
        return error
    return redirect("/teacher-dashboard")


@app.route("/admin-students")
def admin_students():

    admin_id = session.get("admin_id")

    if not admin_id:
        return redirect("/admin-login")

    search = request.args.get("search", "").strip()

    if search:
        students = Student.query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%"))
        ).order_by(Student.roll_number).all()
    else:
        students = Student.query.order_by(Student.roll_number).all()

    return render_template(
        "admin_students.html",
        students=students,
        search=search
    )

@app.route("/admin-add-teacher", methods=["POST"])
def admin_add_teacher():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    name=request.form.get("name","").strip()
    username=request.form.get("username","").strip()
    password=request.form.get("password","").strip()
    subject=request.form.get("subject","").strip()
    groups=request.form.getlist("groups")
    if not name or not username or not password or not subject or not groups:
        return "All teacher fields are required."
    if Teacher.query.filter_by(username=username).first():
        return "This teacher username already exists."
    teacher=Teacher(name=name,username=username,password=password,subject=subject,groups=",".join(groups))
    db.session.add(teacher)
    notify_admin(f"Admin added teacher {name} for {', '.join(groups)}", "admin", "ALL")
    db.session.commit()
    return redirect("/admin-teachers")


@app.route("/admin-teachers")
def admin_teachers():
    admin_id = session.get("admin_id")

    if not admin_id:
        return redirect("/admin-login")

    teachers = Teacher.query.order_by(Teacher.name).all()

    return render_template(
        "admin_teachers.html",
        teachers=teachers
    )


# =========================================================
# ADMIN ACADEMIC MANAGEMENT PAGES
# =========================================================

def admin_guard():
    if not session.get("admin_id"):
        return None, redirect("/admin-login")
    admin = db.session.get(Admin, session.get("admin_id"))
    if admin is None:
        session.clear()
        return None, redirect("/admin-login")
    return admin, None


@app.route("/admin-attendance")
def admin_attendance():
    admin, response = admin_guard()
    if response: return response
    records = Attendance.query.order_by(Attendance.id.desc()).limit(200).all()

    # Normalize mixed attendance date formats for admin display/sorting.
    from datetime import datetime as _admin_attendance_datetime

    def _admin_attendance_date_value(record):
        raw = record.attendance_date
        if hasattr(raw, "strftime"):
            return raw
        raw = str(raw).strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return _admin_attendance_datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return _admin_attendance_datetime.min

    records.sort(key=_admin_attendance_date_value, reverse=True)
    for record in records:
        parsed_date = _admin_attendance_date_value(record)
        record.display_date = (
            parsed_date.strftime("%d/%m/%y")
            if parsed_date != _admin_attendance_datetime.min
            else str(record.attendance_date)
        )

    return render_template("admin_attendance.html", admin=admin, records=records)


@app.route("/admin-timetable")
def admin_timetable():
    admin, response = admin_guard()
    if response: return response
    rows = TimetableData.query.order_by(TimetableData.id.desc()).all()
    return render_template("admin_timetable.html", admin=admin, rows=rows)


@app.route("/admin-marks")
def admin_marks():
    admin, response = admin_guard()
    if response: return response
    records = Marks.query.order_by(Marks.id.desc()).limit(200).all()
    return render_template("admin_marks.html", admin=admin, records=records)


@app.route("/admin-results")
def admin_results():
    admin, response = admin_guard()
    if response: return response
    students = Student.query.order_by(Student.year, Student.group_name, Student.roll_number).all()
    result_counts = {s.id: Marks.query.filter_by(student_id=s.id).count() for s in students}
    return render_template("admin_results.html", admin=admin, students=students, result_counts=result_counts)


@app.route("/admin-notices")
def admin_notices():
    admin, response = admin_guard()
    if response: return response
    notices = Notice.query.order_by(Notice.id.desc()).all()
    return render_template("admin_notices.html", admin=admin, notices=notices)


@app.route("/admin-assignments")
def admin_assignments():
    admin, response = admin_guard()
    if response: return response
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return render_template("admin_assignments.html", admin=admin, assignments=assignments)


@app.route("/admin-study-materials")
def admin_study_materials():
    admin, response = admin_guard()
    if response: return response
    pdfs = PDF.query.order_by(PDF.id.desc()).all()
    return render_template("admin_study_materials.html", admin=admin, pdfs=pdfs)


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.clear()

    return redirect("/admin-login")
# =========================================================
# STUDENT PROFILE
# =========================================================

@app.route("/profile")
def profile():

    student_id = session.get("student_id")

    if not student_id:
        return redirect("/")

    student = db.session.get(
        Student,
        student_id
    )

    if student is None:
        session.clear()
        return redirect("/")

    return render_template(
        "student_account.html",
        student=student
    )
# =========================================================
# CREATE ASSIGNMENT ATTACHMENT TABLE
# =========================================================

with app.app_context():
    AssignmentAttachment.__table__.create(
        db.engine,
        checkfirst=True
    )
# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )