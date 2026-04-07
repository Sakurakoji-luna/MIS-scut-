import sys
import pymysql
import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from PySide6 import QtWidgets, QtCore, QtGui

# ================= 安全性：动态定位 .env =================
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    load_dotenv(str(env_path))
else:
    print(f"CRITICAL ERROR: .env file not found at {env_path}")

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

if not all([DB_HOST, DB_USER, DB_NAME]):
    print("ERROR: .env variables are missing! Please check DB_HOST, DB_USER, etc.")

DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASS,
    'database': DB_NAME,
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

today = datetime.datetime.today()
userID = ""
userChar = ""
specific_character = ['\\', '/', ':', '?', "\"", "\'", "<", ">", "|"]

# ================= 数据库初始化 =================
def Initialize_Database():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                print("开始初始化数据库...")
                # 禁用外键检查以便干净地删除旧表
                cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
                cursor.execute('DROP TABLE IF EXISTS CourseChoosing;')
                cursor.execute('DROP TABLE IF EXISTS Courses;')
                cursor.execute('DROP TABLE IF EXISTS Teachers;')
                cursor.execute('DROP TABLE IF EXISTS Students;')
                cursor.execute('DROP TABLE IF EXISTS AccountPassword;')
                cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')

                # 1. 创建表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Students (
                        StudentID VARCHAR(10) PRIMARY KEY,
                        StudentName VARCHAR(50) NOT NULL,
                        Sex VARCHAR(10),
                        EntranceAge INTEGER,
                        EntranceYear INTEGER NOT NULL,
                        Class VARCHAR(50) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Teachers (
                        TeacherID VARCHAR(5) PRIMARY KEY,
                        TeacherName VARCHAR(50) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Courses (
                        CourseID VARCHAR(7) PRIMARY KEY,
                        CourseName VARCHAR(100) NOT NULL,
                        TeacherID VARCHAR(5) NOT NULL,
                        Credit FLOAT NOT NULL,
                        Grade INTEGER NOT NULL,
                        CanceledYear INTEGER,
                        CONSTRAINT fk_courses_teacher FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS CourseChoosing (
                        StudentID VARCHAR(10) NOT NULL,
                        CourseID VARCHAR(7) NOT NULL,
                        TeacherID VARCHAR(5) NOT NULL,
                        ChosenYear INTEGER NOT NULL,
                        Score FLOAT,
                        PRIMARY KEY (StudentID, CourseID, TeacherID),
                        CONSTRAINT fk_cc_student FOREIGN KEY (StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE,
                        CONSTRAINT fk_cc_course FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
                        CONSTRAINT fk_cc_teacher FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS AccountPassword (
                        Account VARCHAR(20) PRIMARY KEY,
                        Occupation VARCHAR(20),
                        Password VARCHAR(50) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')

                # 2. 插入初始数据
                cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')

                students = [
                    ('2022000001', 'Alice', 'female', 18, 2022, 'Class 1'),
                    ('2022000002', 'Jack', 'male', 19, 2022, 'Class 1'),
                    ('2022000003', 'Rose', 'female', 18, 2022, 'Class 1'),
                    ('2021000001', 'Bob', 'male', 20, 2021, 'Class 2'),
                    ('2020000001', 'Charlie', 'male', 22, 2020, 'Class 3')
                ]
                cursor.executemany('INSERT INTO Students VALUES (%s, %s, %s, %s, %s, %s)', students)

                teachers = [('00001', 'Smith'), ('00002', 'Johnson'), ('00003', 'Williams')]
                cursor.executemany('INSERT INTO Teachers VALUES (%s, %s)', teachers)

                courses = [
                    ('0000001', 'Mathematical analysis', '00001', 4, 1, None),
                    ('0000002', 'Python Program', '00002', 3, 1, None),
                    ('0000003', 'C++ Program', '00003', 2, 2, 2023)
                ]
                cursor.executemany('INSERT INTO Courses VALUES (%s, %s, %s, %s, %s, %s)', courses)

                course_choosing = [
                    ('2020000001', '0000001', '00001', 2022, 78.0),
                    ('2020000001', '0000002', '00002', 2021, 100.0),
                    ('2020000001', '0000003', '00003', 2020, 60.0),
                    ('2021000001', '0000002', '00002', 2022, 90.0),
                    ('2021000001', '0000003', '00003', 2021, 99.0),
                    ('2022000001', '0000003', '00003', 2022, 95.0),
                    ('2022000002', '0000003', '00003', 2022, 88.5),
                    ('2022000003', '0000003', '00003', 2022, 78.0)
                ]
                cursor.executemany('INSERT INTO CourseChoosing VALUES (%s, %s, %s, %s, %s)', course_choosing)

                account_passwords = [
                    ('2020000001', 'student', '123456'), ('2021000001', 'student', '123456'),
                    ('2022000001', 'student', '123456'), ('2022000002', 'student', '123456'),
                    ('2022000003', 'student', '123456'), ('00001', 'teacher', '123456'),
                    ('00002', 'teacher', '123456'), ('00003', 'teacher', '123456'),
                    ('00000', 'admin', '123456')
                ]
                cursor.executemany('INSERT INTO AccountPassword VALUES (%s, %s, %s)', account_passwords)
                
                cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
            conn.commit()
            print("=== 数据库自动重置并初始化成功！===")
    except Exception as e:
        print(f"Database Initialization Error: {e}")

# ================= UI 界面代码 =================

class Login_Ui(QtWidgets.QWidget):
    admin_window = QtCore.Signal()
    teacher_window = QtCore.Signal()
    student_window = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(500, 320)
        
        self.label_Welcome = QtWidgets.QLabel("Welcome to MIS for Computer\nScience college of SCUT", self)
        self.label_Welcome.setGeometry(QtCore.QRect(100, 20, 300, 60))
        self.label_Welcome.setAlignment(QtCore.Qt.AlignCenter)
        
        QtWidgets.QLabel("User ID", self).setGeometry(QtCore.QRect(98, 93, 70, 40))
        self.User_ID_Input = QtWidgets.QLineEdit(self)
        self.User_ID_Input.setGeometry(QtCore.QRect(170, 100, 200, 25))
        
        QtWidgets.QLabel("Password", self).setGeometry(QtCore.QRect(98, 133, 70, 40))
        self.Password_Input = QtWidgets.QLineEdit(self)
        self.Password_Input.setGeometry(QtCore.QRect(170, 140, 200, 25))
        self.Password_Input.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.Button_login = QtWidgets.QPushButton("Login", self)
        self.Button_login.setGeometry(QtCore.QRect(200, 180, 100, 30))
        self.Button_login.clicked.connect(self.login_check)

        self.label_Invalid_Login_Error = QtWidgets.QLabel(self)
        self.label_Invalid_Login_Error.setGeometry(QtCore.QRect(40, 220, 420, 60))
        self.label_Invalid_Login_Error.setWordWrap(True) 
        self.label_Invalid_Login_Error.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.label_Invalid_Login_Error.setStyleSheet("color: red; font-size: 10pt;")
        self.label_Invalid_Login_Error.setVisible(False)
        
        self.label_author = QtWidgets.QLabel("作者：计算机科学与技术(全英创新班) 胡子健", self)
        self.label_author.setGeometry(QtCore.QRect(0, 280, 500, 30))
        self.label_author.setAlignment(QtCore.Qt.AlignCenter)

    def login_check(self):
        global userID, userChar
        getID = self.User_ID_Input.text()
        if not getID.isdigit():
            self.label_Invalid_Login_Error.setText("User ID must be a decimal number\nplease try again")
            self.label_Invalid_Login_Error.setVisible(True)
            return
            
        getPW = self.Password_Input.text()
        if getPW == "":
            self.label_Invalid_Login_Error.setText("Password should not be empty")
            self.label_Invalid_Login_Error.setVisible(True)
            return
            
        for i in getPW:
            if i in specific_character:
                self.label_Invalid_Login_Error.setText("Password should not contain special chars")
                self.label_Invalid_Login_Error.setVisible(True)
                return

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT Occupation, Password FROM AccountPassword WHERE Account=%s", (getID,))
                    result = cursor.fetchone()

            if result and str(result[1]) == getPW:
                userID = getID
                userChar = result[0]
                if userChar == "admin":
                    self.admin_window.emit()
                elif userChar == "teacher":
                    self.teacher_window.emit()
                elif userChar == "student":
                    self.student_window.emit()
            else:
                self.label_Invalid_Login_Error.setText("User ID or Password incorrect please try again")
                self.label_Invalid_Login_Error.setVisible(True)
        except Exception as e:
            self.label_Invalid_Login_Error.setText(f"DB Error: {e}")
            self.label_Invalid_Login_Error.setVisible(True)

class Student_Ui(QtWidgets.QWidget):
    logout = QtCore.Signal()
    query = QtCore.Signal()
    change = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student")
        self.resize(541, 365)
        
        self.btn_query = QtWidgets.QPushButton("Query", self)
        self.btn_query.setGeometry(QtCore.QRect(180, 90, 161, 61))
        self.btn_query.clicked.connect(self.query.emit)
        
        self.btn_change = QtWidgets.QPushButton("Change Password", self)
        self.btn_change.setGeometry(QtCore.QRect(180, 160, 161, 61))
        self.btn_change.clicked.connect(self.change.emit)

        self.btn_logout = QtWidgets.QPushButton("Logout", self)
        self.btn_logout.setGeometry(QtCore.QRect(180, 230, 161, 61))
        self.btn_logout.clicked.connect(self.logout.emit)

class Teacher_Ui(QtWidgets.QWidget):
    query = QtCore.Signal()
    sss = QtCore.Signal()
    cp = QtCore.Signal()
    lo = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teacher")
        self.resize(541, 365)
        
        self.btn_query = QtWidgets.QPushButton("Query", self)
        self.btn_query.setGeometry(QtCore.QRect(120, 50, 281, 61))
        self.btn_query.clicked.connect(self.query.emit)
        
        self.btn_sss = QtWidgets.QPushButton("Set Student's Score", self)
        self.btn_sss.setGeometry(QtCore.QRect(120, 120, 281, 61))
        self.btn_sss.clicked.connect(self.sss.emit)
        
        self.btn_cp = QtWidgets.QPushButton("Change Password", self)
        self.btn_cp.setGeometry(QtCore.QRect(120, 190, 281, 61))
        self.btn_cp.clicked.connect(self.cp.emit)

        self.btn_logout = QtWidgets.QPushButton("Logout", self)
        self.btn_logout.setGeometry(QtCore.QRect(120, 260, 281, 61))
        self.btn_logout.clicked.connect(self.lo.emit)

class Admin_Ui(QtWidgets.QWidget):
    query = QtCore.Signal()
    mi = QtCore.Signal()
    cp = QtCore.Signal()
    logout = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin")
        self.resize(541, 380)
        
        self.btn_query = QtWidgets.QPushButton("Query", self)
        self.btn_query.setGeometry(QtCore.QRect(170, 20, 181, 60))
        self.btn_query.clicked.connect(self.query.emit)
        
        self.btn_modify = QtWidgets.QPushButton("Modify Information", self)
        self.btn_modify.setGeometry(QtCore.QRect(170, 90, 181, 60))
        self.btn_modify.clicked.connect(self.mi.emit)
        
        self.btn_cp = QtWidgets.QPushButton("Change Password", self)
        self.btn_cp.setGeometry(QtCore.QRect(170, 160, 181, 60))
        self.btn_cp.clicked.connect(self.cp.emit)
        
        self.btn_init = QtWidgets.QPushButton("Initialize\nDatabase", self)
        self.btn_init.setGeometry(QtCore.QRect(170, 230, 181, 60))
        self.btn_init.clicked.connect(self.initialize_database)
        
        self.btn_logout = QtWidgets.QPushButton("Logout", self)
        self.btn_logout.setGeometry(QtCore.QRect(170, 300, 181, 60))
        self.btn_logout.clicked.connect(self.logout.emit)

    def initialize_database(self):
        reply = QtWidgets.QMessageBox.question(self, 'Initialize Database', 'Are you sure to initialize the database?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            Initialize_Database()
            QtWidgets.QMessageBox.information(self, "Success", "Database Initialized.")

class Query_Ui(QtWidgets.QWidget):
    stu_info = QtCore.Signal()
    stu_score = QtCore.Signal()
    cou_info = QtCore.Signal()
    ave_score = QtCore.Signal()
    ti = QtCore.Signal()
    bs = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Query")
        self.resize(451, 330)
        
        buttons = [
            ("Student Info", self.stu_info, 20),
            ("Student Score Info", self.stu_score, 70),
            ("Course (Choosing) Info", self.cou_info, 120),
            ("Teacher (Teaching) Info", self.ti, 170),
            ("Average Score Info", self.ave_score, 220),
            ("Back", self.bs, 270)
        ]
        
        for text, signal, y in buttons:
            btn = QtWidgets.QPushButton(text, self)
            btn.setGeometry(QtCore.QRect(100, y, 231, 40))
            btn.clicked.connect(signal.emit)

# 辅助函数：快速填充 QTableWidget 数据
def fill_table(tableWidget, cursor, results):
    if len(results) == 0:
        tableWidget.clear()
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(0)
        return False
        
    col_names = [d[0] for d in cursor.description]
    tableWidget.setColumnCount(len(col_names))
    tableWidget.setRowCount(len(results))
    tableWidget.setHorizontalHeaderLabels(col_names)
    
    for row_idx, row_data in enumerate(results):
        for col_idx, value in enumerate(row_data):
            tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))
    return True

class Student_Info_Query_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Info Query")
        self.resize(700, 350)
        
        QtWidgets.QLabel("Student ID", self).setGeometry(QtCore.QRect(20, 30, 120, 20))
        QtWidgets.QLabel("Student Name", self).setGeometry(QtCore.QRect(20, 90, 120, 20))
        self.label_Result = QtWidgets.QLabel("Query Result", self)
        self.label_Result.setGeometry(QtCore.QRect(0, 150, 700, 20))
        self.label_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Result.setStyleSheet("color: red;")
        
        self.line_id = QtWidgets.QLineEdit(self)
        self.line_id.setGeometry(QtCore.QRect(160, 30, 300, 20))
        self.line_name = QtWidgets.QLineEdit(self)
        self.line_name.setGeometry(QtCore.QRect(160, 90, 300, 20))
        
        self.btn_stu = QtWidgets.QPushButton("Student Info", self)
        self.btn_stu.setGeometry(QtCore.QRect(480, 30, 200, 30))
        self.btn_stu.clicked.connect(self.query_student)
        
        self.btn_cou = QtWidgets.QPushButton("Chosen Course Info", self)
        self.btn_cou.setGeometry(QtCore.QRect(480, 70, 200, 30))
        self.btn_cou.clicked.connect(self.query_course)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(480, 110, 200, 30))
        self.btn_back.clicked.connect(self.back.emit)
        
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(20, 170, 660, 170))

    def execute_and_fill(self, sql, params=()):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    if fill_table(self.table, cursor, results):
                        self.label_Result.setText("Query Result")
                    else:
                        self.label_Result.setText("There is no data")
        except Exception as e:
            self.label_Result.setText(f"Error: {e}")

    def query_student(self):
        s_id, s_name = self.line_id.text(), self.line_name.text()
        sql, params = "SELECT * FROM Students WHERE 1=1", []
        if s_id: 
            sql += " AND StudentID=%s"
            params.append(s_id)
        if s_name:
            sql += " AND StudentName=%s"
            params.append(s_name)
        sql += " ORDER BY StudentID"
        self.execute_and_fill(sql, params)

    def query_course(self):
        s_id, s_name = self.line_id.text(), self.line_name.text()
        sql, params = "SELECT DISTINCT c.* FROM Courses c JOIN CourseChoosing cc ON c.CourseID = cc.CourseID JOIN Students s ON cc.StudentID = s.StudentID WHERE 1=1", []
        if s_id:
            sql += " AND s.StudentID=%s"
            params.append(s_id)
        if s_name:
            sql += " AND s.StudentName=%s"
            params.append(s_name)
        sql += " ORDER BY c.CourseID"
        self.execute_and_fill(sql, params)

class Student_Score_Query_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Score Info Query")
        self.resize(700, 350)
        
        labels = ["Student ID", "Student Name", "Course ID", "Course Name"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(20, 30 + i*30, 120, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(160, 30 + i*30, 300, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("Query Result", self)
        self.label_Result.setGeometry(QtCore.QRect(255, 150, 200, 20))
        self.label_Result.setStyleSheet("color: red;")
        
        self.btn_query_score = QtWidgets.QPushButton("Student Score Info", self)
        self.btn_query_score.setGeometry(QtCore.QRect(480, 30, 200, 30))
        self.btn_query_score.clicked.connect(self.query)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(480, 110, 200, 30))
        self.btn_back.clicked.connect(self.back.emit)
        
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(20, 170, 660, 170))

        # --- 核心体验优化：学生自动填光学号并锁定，防止查别人成绩 ---
        if userChar == "student":
            self.inputs["Student ID"].setText(userID)
            self.inputs["Student ID"].setReadOnly(True)
            self.inputs["Student ID"].setStyleSheet("background-color: #e0e0e0; color: gray;")
            # 一进入界面自动查成绩
            QtCore.QTimer.singleShot(10, self.query)

    def query(self):
        sql = '''SELECT s.StudentName, s.StudentID, c.CourseName, c.CourseID, cc.Score
                 FROM Students s
                 JOIN CourseChoosing cc ON s.StudentID=cc.StudentID
                 JOIN Courses c ON c.CourseID=cc.CourseID WHERE 1=1'''
        params = []
        
        s_id = self.inputs["Student ID"].text().strip()
        s_name = self.inputs["Student Name"].text().strip()
        c_id = self.inputs["Course ID"].text().strip()
        c_name = self.inputs["Course Name"].text().strip()
        
        if s_id: sql += " AND s.StudentID=%s"; params.append(s_id)
        if s_name: sql += " AND s.StudentName=%s"; params.append(s_name)
        if c_id: sql += " AND c.CourseID=%s"; params.append(c_id)
        if c_name: sql += " AND c.CourseName=%s"; params.append(c_name)
        
        sql += " ORDER BY s.StudentID, c.CourseID"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    if fill_table(self.table, cursor, cursor.fetchall()):
                        self.label_Result.setText("Query Result")
                    else:
                        self.label_Result.setText("There is no data")
        except Exception as e:
            self.label_Result.setText("Database Error")
   


# ================= 补充缺失的空壳查询界面 =================
class Course_Info_Query_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Course Info Query")
        self.resize(700, 350)
        
        labels = ["Course ID", "Course Name", "Teacher Name"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(20, 30 + i*40, 100, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(130, 30 + i*40, 200, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("Query Result", self)
        self.label_Result.setGeometry(QtCore.QRect(350, 140, 200, 20))
        self.label_Result.setStyleSheet("color: red;")
        
        self.btn_query = QtWidgets.QPushButton("Query Course", self)
        self.btn_query.setGeometry(QtCore.QRect(400, 30, 150, 35))
        self.btn_query.clicked.connect(self.query)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(400, 80, 150, 35))
        self.btn_back.clicked.connect(self.back.emit)
        
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(20, 170, 660, 160))

        # --- 核心体验优化：如果是学生登录，自动查询并调整界面 ---
        if userChar == "student":
            self.setWindowTitle("My Chosen Courses")
            self.btn_query.setText("Filter My Courses")
            # 延时 10 毫秒自动执行查询（确保界面先画完再查数据库，防止卡顿）
            QtCore.QTimer.singleShot(10, self.query)

    def query(self):
        # 针对不同角色使用不同的 SQL
        if userChar == "student":
            # 学生：必须关联 CourseChoosing 表，且只查自己的 userID
            sql = '''SELECT c.CourseID, c.CourseName, t.TeacherName, c.Credit, c.Grade, cc.ChosenYear
                     FROM CourseChoosing cc
                     JOIN Courses c ON cc.CourseID = c.CourseID
                     LEFT JOIN Teachers t ON c.TeacherID = t.TeacherID
                     WHERE cc.StudentID = %s'''
            params = [userID]
        else:
            # 老师/管理员：直接查全校的所有课程库
            sql = '''SELECT c.CourseID, c.CourseName, t.TeacherName, c.Credit, c.Grade, c.CanceledYear
                     FROM Courses c
                     LEFT JOIN Teachers t ON c.TeacherID = t.TeacherID
                     WHERE 1=1'''
            params = []
        
        # 在查出来的范围内，还可以继续使用输入框进行二次过滤
        c_id = self.inputs["Course ID"].text().strip()
        c_name = self.inputs["Course Name"].text().strip()
        t_name = self.inputs["Teacher Name"].text().strip()
        
        if c_id: sql += " AND c.CourseID=%s"; params.append(c_id)
        if c_name: sql += " AND c.CourseName LIKE %s"; params.append(f"%{c_name}%")
        if t_name: sql += " AND t.TeacherName LIKE %s"; params.append(f"%{t_name}%")
        
        sql += " ORDER BY c.CourseID"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    if fill_table(self.table, cursor, cursor.fetchall()):
                        self.label_Result.setText("Query Result")
                    else:
                        self.label_Result.setText("There is no data")
        except Exception as e:
            self.label_Result.setText(f"Database Error: {e}")


    
   

class Teaching_Info_Query_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teacher & Teaching Info Query")
        self.resize(700, 350)
        
        labels = ["Teacher ID", "Teacher Name"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(20, 40 + i*50, 100, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(130, 40 + i*50, 200, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("Query Result", self)
        self.label_Result.setGeometry(QtCore.QRect(350, 130, 200, 20))
        self.label_Result.setStyleSheet("color: red;")
        
        self.btn_query = QtWidgets.QPushButton("Query Teaching Info", self)
        self.btn_query.setGeometry(QtCore.QRect(400, 30, 180, 35))
        self.btn_query.clicked.connect(self.query)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(400, 80, 180, 35))
        self.btn_back.clicked.connect(self.back.emit)
        
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(20, 160, 660, 170))

    def query(self):
        sql = '''SELECT t.TeacherID, t.TeacherName, c.CourseID, c.CourseName, c.Credit
                 FROM Teachers t
                 JOIN Courses c ON t.TeacherID = c.TeacherID
                 WHERE 1=1'''
        params = []
        
        t_id = self.inputs["Teacher ID"].text().strip()
        t_name = self.inputs["Teacher Name"].text().strip()
        
        if t_id: sql += " AND t.TeacherID=%s"; params.append(t_id)
        if t_name: sql += " AND t.TeacherName LIKE %s"; params.append(f"%{t_name}%")
        
        sql += " ORDER BY t.TeacherID, c.CourseID"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    if fill_table(self.table, cursor, cursor.fetchall()):
                        self.label_Result.setText("Query Result")
                    else:
                        self.label_Result.setText("There is no data")
        except Exception as e:
            self.label_Result.setText(f"Database Error: {e}")
    back = QtCore.Signal()


class Average_Score_Info_Query_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Average Score Info Query")
        self.resize(700, 350)
        
        QtWidgets.QLabel("Course ID", self).setGeometry(QtCore.QRect(20, 40, 100, 20))
        self.line_c_id = QtWidgets.QLineEdit(self)
        self.line_c_id.setGeometry(QtCore.QRect(130, 40, 200, 20))
        
        QtWidgets.QLabel("Course Name", self).setGeometry(QtCore.QRect(20, 90, 100, 20))
        self.line_c_name = QtWidgets.QLineEdit(self)
        self.line_c_name.setGeometry(QtCore.QRect(130, 90, 200, 20))
            
        self.label_Result = QtWidgets.QLabel("Query Result", self)
        self.label_Result.setGeometry(QtCore.QRect(350, 130, 200, 20))
        self.label_Result.setStyleSheet("color: red;")
        
        self.btn_query = QtWidgets.QPushButton("Query Average", self)
        self.btn_query.setGeometry(QtCore.QRect(400, 30, 150, 35))
        self.btn_query.clicked.connect(self.query)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(400, 80, 150, 35))
        self.btn_back.clicked.connect(self.back.emit)
        
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(20, 160, 660, 170))

    def query(self):
        # 使用聚合函数计算人数、平均分（保留两位小数）、最高分和最低分
        sql = '''SELECT c.CourseID, c.CourseName, 
                        COUNT(cc.StudentID) as StudentCount,
                        ROUND(AVG(cc.Score), 2) as AverageScore,
                        MAX(cc.Score) as MaxScore,
                        MIN(cc.Score) as MinScore
                 FROM Courses c
                 JOIN CourseChoosing cc ON c.CourseID = cc.CourseID
                 WHERE cc.Score IS NOT NULL '''
        params = []
        
        c_id = self.line_c_id.text().strip()
        c_name = self.line_c_name.text().strip()
        
        if c_id: sql += " AND c.CourseID=%s"; params.append(c_id)
        if c_name: sql += " AND c.CourseName LIKE %s"; params.append(f"%{c_name}%")
        
        # 使用 GROUP BY 按课程分组
        sql += " GROUP BY c.CourseID, c.CourseName ORDER BY c.CourseID"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    if fill_table(self.table, cursor, cursor.fetchall()):
                        self.label_Result.setText("Query Result")
                    else:
                        self.label_Result.setText("There is no data")
        except Exception as e:
            self.label_Result.setText(f"Database Error: {e}")
    back = QtCore.Signal()

# ================= 修改与操作界面 =================
class Modify_Info_Ui(QtWidgets.QWidget):
    stu_info = QtCore.Signal()
    cou_info = QtCore.Signal()
    coc_info = QtCore.Signal()
    bs = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Information")
        self.resize(451, 313)
        
        self.btn_stu = QtWidgets.QPushButton("Student Info", self)
        self.btn_stu.setGeometry(QtCore.QRect(120, 60, 191, 41))
        self.btn_stu.clicked.connect(self.stu_info.emit)
        
        self.btn_cou = QtWidgets.QPushButton("Course Info", self)
        self.btn_cou.setGeometry(QtCore.QRect(120, 110, 191, 41))
        self.btn_cou.clicked.connect(self.cou_info.emit)
        
        self.btn_coc = QtWidgets.QPushButton("Course Choosing Info", self)
        self.btn_coc.setGeometry(QtCore.QRect(120, 160, 191, 41))
        self.btn_coc.clicked.connect(self.coc_info.emit)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(120, 210, 191, 41))
        self.btn_back.clicked.connect(self.bs.emit)

# 补充缺失的空壳修改界面
class Student_Info_Modify_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Student Info")
        self.resize(700, 400)
        
        # 1. 动态生成表单输入框
        labels = ["StudentID", "StudentName", "Sex", "EntranceAge", "EntranceYear", "Class"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(50, 30 + i*40, 100, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(150, 30 + i*40, 200, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("", self)
        self.label_Result.setGeometry(QtCore.QRect(0, 280, 700, 30))
        self.label_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Result.setStyleSheet("font-weight: bold;")
        
        # 2. 核心操作按钮
        self.btn_add = QtWidgets.QPushButton("Add", self)
        self.btn_add.setGeometry(QtCore.QRect(420, 50, 150, 35))
        self.btn_add.clicked.connect(self.add_student)
        
        self.btn_update = QtWidgets.QPushButton("Update", self)
        self.btn_update.setGeometry(QtCore.QRect(420, 110, 150, 35))
        self.btn_update.clicked.connect(self.update_student)

        self.btn_delete = QtWidgets.QPushButton("Delete", self)
        self.btn_delete.setGeometry(QtCore.QRect(420, 170, 150, 35))
        self.btn_delete.clicked.connect(self.delete_student)
        self.btn_delete.setStyleSheet("color: red;") # 删除按钮标红预警
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(420, 230, 150, 35))
        self.btn_back.clicked.connect(self.back.emit)

    def execute_modify(self, sql, params, success_msg):
        """统一封装的数据库修改执行器"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText(success_msg)
        except pymysql.err.IntegrityError as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Data Conflict Error (Duplicate ID or Foreign Key): {e.args[1]}")
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")

    def add_student(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not all(vals[:2]) or not vals[4]: # ID, Name, EntranceYear 不能为空
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: StudentID, Name and EntranceYear are required!")
            return
        
        student_id = vals[0]
        default_password = "123456" # 设置统一的初始默认密码
        
        try:
            # 开启数据库连接，这里会自动处理事务 (Transaction)
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 第一步：把学生基本信息存入 Students 表
                    sql_student = "INSERT INTO Students VALUES (%s, %s, %s, %s, %s, %s)"
                    params_student = [vals[0], vals[1], vals[2] or None, vals[3] or None, vals[4], vals[5] or 'None']
                    cursor.execute(sql_student, params_student)
                    
                    # 第二步：同时为该新生在 AccountPassword 表中创建登录账号
                    sql_account = "INSERT INTO AccountPassword (Account, Occupation, Password) VALUES (%s, %s, %s)"
                    cursor.execute(sql_account, (student_id, 'student', default_password))
                    
                    # 只有两步都执行成功，才会将数据一起提交保存 (Commit)
                    conn.commit() 
                    
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText(f"Success! Default password is {default_password}")
                    
        except pymysql.err.IntegrityError as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Data Conflict Error (Duplicate ID): {e.args[1]}")
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")

    def update_student(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not vals[0]:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: StudentID is required to locate the student.")
            return
        sql = '''UPDATE Students SET StudentName=IFNULL(%s, StudentName), Sex=IFNULL(%s, Sex), 
                 EntranceAge=IFNULL(%s, EntranceAge), EntranceYear=IFNULL(%s, EntranceYear), 
                 Class=IFNULL(%s, Class) WHERE StudentID=%s'''
        params = [vals[1] or None, vals[2] or None, vals[3] or None, vals[4] or None, vals[5] or None, vals[0]]
        self.execute_modify(sql, params, "Student updated successfully!")

    def delete_student(self):
        s_id = self.inputs["StudentID"].text().strip()
        if not s_id:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: Please specify the StudentID to delete.")
            return
            
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 先删除登录账号
                    cursor.execute("DELETE FROM AccountPassword WHERE Account=%s AND Occupation='student'", (s_id,))
                    # 再删除学生信息 (因为有级联删除，相关的选课记录也会被自动删除)
                    cursor.execute("DELETE FROM Students WHERE StudentID=%s", (s_id,))
                    
                    conn.commit()
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText("Student and account deleted successfully!")
                    
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")

class Course_Info_Modify_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Course Info")
        self.resize(700, 400)
        
        labels = ["CourseID", "CourseName", "TeacherID", "Credit", "Grade", "CanceledYear"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(50, 30 + i*40, 100, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(150, 30 + i*40, 200, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("", self)
        self.label_Result.setGeometry(QtCore.QRect(0, 280, 700, 30))
        self.label_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Result.setStyleSheet("font-weight: bold;")
        
        self.btn_add = QtWidgets.QPushButton("Add", self)
        self.btn_add.setGeometry(QtCore.QRect(420, 50, 150, 35))
        self.btn_add.clicked.connect(self.add_course)
        
        self.btn_update = QtWidgets.QPushButton("Update", self)
        self.btn_update.setGeometry(QtCore.QRect(420, 110, 150, 35))
        self.btn_update.clicked.connect(self.update_course)

        self.btn_delete = QtWidgets.QPushButton("Delete", self)
        self.btn_delete.setGeometry(QtCore.QRect(420, 170, 150, 35))
        self.btn_delete.clicked.connect(self.delete_course)
        self.btn_delete.setStyleSheet("color: red;")
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(420, 230, 150, 35))
        self.btn_back.clicked.connect(self.back.emit)

    def execute_modify(self, sql, params, success_msg):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText(success_msg)
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")

    def add_course(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not all(vals[:5]): # 前5个字段必填
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: CourseID, Name, TeacherID, Credit, Grade are required!")
            return
        sql = "INSERT INTO Courses VALUES (%s, %s, %s, %s, %s, %s)"
        params = [vals[0], vals[1], vals[2], vals[3], vals[4], vals[5] or None]
        self.execute_modify(sql, params, "Course added successfully!")

    def update_course(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not vals[0]:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: CourseID is required to locate the course.")
            return
        sql = '''UPDATE Courses SET CourseName=IFNULL(%s, CourseName), TeacherID=IFNULL(%s, TeacherID), 
                 Credit=IFNULL(%s, Credit), Grade=IFNULL(%s, Grade), CanceledYear=%s 
                 WHERE CourseID=%s'''
        # 注意 CanceledYear 如果为空，应该用 None 覆盖，表示没取消
        params = [vals[1] or None, vals[2] or None, vals[3] or None, vals[4] or None, vals[5] or None, vals[0]]
        self.execute_modify(sql, params, "Course updated successfully!")

    def delete_course(self):
        c_id = self.inputs["CourseID"].text().strip()
        if not c_id:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: Please specify the CourseID to delete.")
            return
        sql = "DELETE FROM Courses WHERE CourseID=%s"
        self.execute_modify(sql, [c_id], "Course deleted successfully!")
    back = QtCore.Signal()


class Course_Choosing_Info_Modify_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Course Choosing Info")
        self.resize(700, 360)
        
        labels = ["StudentID", "CourseID", "TeacherID", "ChosenYear", "Score"]
        self.inputs = {}
        for i, text in enumerate(labels):
            QtWidgets.QLabel(text, self).setGeometry(QtCore.QRect(50, 30 + i*40, 100, 20))
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(QtCore.QRect(150, 30 + i*40, 200, 20))
            self.inputs[text] = le
            
        self.label_Result = QtWidgets.QLabel("", self)
        self.label_Result.setGeometry(QtCore.QRect(0, 250, 700, 30))
        self.label_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Result.setStyleSheet("font-weight: bold;")
        
        self.btn_add = QtWidgets.QPushButton("Add", self)
        self.btn_add.setGeometry(QtCore.QRect(420, 50, 150, 35))
        self.btn_add.clicked.connect(self.add_cc)
        
        self.btn_update = QtWidgets.QPushButton("Update", self)
        self.btn_update.setGeometry(QtCore.QRect(420, 110, 150, 35))
        self.btn_update.clicked.connect(self.update_cc)

        self.btn_delete = QtWidgets.QPushButton("Delete", self)
        self.btn_delete.setGeometry(QtCore.QRect(420, 170, 150, 35))
        self.btn_delete.clicked.connect(self.delete_cc)
        self.btn_delete.setStyleSheet("color: red;")
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(420, 230, 150, 35))
        self.btn_back.clicked.connect(self.back.emit)

    def execute_modify(self, sql, params, success_msg):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText(success_msg)
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")

    def add_cc(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not all(vals[:4]): # 前4个为必填（分数可以为空，表示还没考）
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: StudentID, CourseID, TeacherID, ChosenYear are required!")
            return
        sql = "INSERT INTO CourseChoosing VALUES (%s, %s, %s, %s, %s)"
        params = [vals[0], vals[1], vals[2], vals[3], vals[4] or None]
        self.execute_modify(sql, params, "Course Choosing record added!")

    def update_cc(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not all(vals[:3]):
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: StudentID, CourseID, and TeacherID are required to locate record.")
            return
        sql = '''UPDATE CourseChoosing SET ChosenYear=IFNULL(%s, ChosenYear), Score=IFNULL(%s, Score) 
                 WHERE StudentID=%s AND CourseID=%s AND TeacherID=%s'''
        params = [vals[3] or None, vals[4] or None, vals[0], vals[1], vals[2]]
        self.execute_modify(sql, params, "Course Choosing record updated!")

    def delete_cc(self):
        vals = [self.inputs[k].text().strip() for k in self.inputs]
        if not all(vals[:3]):
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Error: StudentID, CourseID, and TeacherID are required to locate record.")
            return
        sql = "DELETE FROM CourseChoosing WHERE StudentID=%s AND CourseID=%s AND TeacherID=%s"
        self.execute_modify(sql, [vals[0], vals[1], vals[2]], "Course Choosing record deleted!")
    back = QtCore.Signal()

class Set_Student_Score_Ui(QtWidgets.QWidget):
    back = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set Student Score")
        self.resize(500, 300)
        
        QtWidgets.QLabel("Student ID", self).setGeometry(QtCore.QRect(50, 40, 100, 20))
        self.line_s_id = QtWidgets.QLineEdit(self)
        self.line_s_id.setGeometry(QtCore.QRect(150, 40, 200, 20))
        
        QtWidgets.QLabel("Course ID", self).setGeometry(QtCore.QRect(50, 90, 100, 20))
        self.line_c_id = QtWidgets.QLineEdit(self)
        self.line_c_id.setGeometry(QtCore.QRect(150, 90, 200, 20))
        
        QtWidgets.QLabel("Score", self).setGeometry(QtCore.QRect(50, 140, 100, 20))
        self.line_score = QtWidgets.QLineEdit(self)
        self.line_score.setGeometry(QtCore.QRect(150, 140, 200, 20))
            
        self.label_Result = QtWidgets.QLabel("", self)
        self.label_Result.setGeometry(QtCore.QRect(0, 180, 500, 30))
        self.label_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Result.setStyleSheet("color: red; font-weight: bold;")
        
        self.btn_update = QtWidgets.QPushButton("Submit Score", self)
        self.btn_update.setGeometry(QtCore.QRect(120, 230, 120, 35))
        self.btn_update.clicked.connect(self.update_score)
        
        self.btn_back = QtWidgets.QPushButton("Back", self)
        self.btn_back.setGeometry(QtCore.QRect(260, 230, 120, 35))
        self.btn_back.clicked.connect(self.back.emit)

    def update_score(self):
        s_id = self.line_s_id.text().strip()
        c_id = self.line_c_id.text().strip()
        score_str = self.line_score.text().strip()
        
        # 1. 基础的输入为空拦截
        if not s_id or not c_id or not score_str:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Please fill in all fields!")
            return
            
        # 2. 分数合法性拦截
        try:
            score = float(score_str)
            if score < 0 or score > 100:
                self.label_Result.setStyleSheet("color: red;")
                self.label_Result.setText("Score must be between 0 and 100.")
                return
        except ValueError:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText("Score must be a valid number.")
            return
            
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 3. 核心校验：验证该老师 (userID) 是否负责该课程，且该学生是否选了这门课
                    check_sql = "SELECT * FROM CourseChoosing WHERE StudentID=%s AND CourseID=%s AND TeacherID=%s"
                    cursor.execute(check_sql, (s_id, c_id, userID))
                    
                    if not cursor.fetchone():
                        self.label_Result.setStyleSheet("color: red;")
                        self.label_Result.setText("Error: This student didn't choose your course\nor IDs are invalid.")
                        return
                    
                    # 4. 校验通过，执行更新
                    update_sql = "UPDATE CourseChoosing SET Score=%s WHERE StudentID=%s AND CourseID=%s AND TeacherID=%s"
                    cursor.execute(update_sql, (score, s_id, c_id, userID))
                    conn.commit()
                    
                    self.label_Result.setStyleSheet("color: green;")
                    self.label_Result.setText("Score updated successfully!")
        except Exception as e:
            self.label_Result.setStyleSheet("color: red;")
            self.label_Result.setText(f"Database Error: {e}")
    back = QtCore.Signal()


class Change_Password_Ui(QtWidgets.QWidget):
    ret = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change Password")
        self.resize(400, 160)
        QtWidgets.QLabel("Original Password", self).setGeometry(QtCore.QRect(10, 20, 160, 20))
        QtWidgets.QLabel("New Password", self).setGeometry(QtCore.QRect(55, 50, 150, 20))
        
        self.line_old = QtWidgets.QLineEdit(self)
        self.line_old.setGeometry(QtCore.QRect(180, 20, 191, 20))
        self.line_new = QtWidgets.QLineEdit(self)
        self.line_new.setGeometry(QtCore.QRect(180, 50, 191, 20))
        
        self.lbl_err = QtWidgets.QLabel(self)
        self.lbl_err.setGeometry(QtCore.QRect(0, 110, 400, 40))
        self.lbl_err.setStyleSheet("color: red;")
        self.lbl_err.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_modify = QtWidgets.QPushButton("Modify", self)
        self.btn_modify.setGeometry(QtCore.QRect(120, 80, 75, 24))
        self.btn_modify.clicked.connect(self.modify)

        self.btn_return = QtWidgets.QPushButton("Return", self)
        self.btn_return.setGeometry(QtCore.QRect(210, 80, 75, 24))
        self.btn_return.clicked.connect(self.ret.emit)

    def modify(self):
        old_pwd = self.line_old.text()
        new_pwd = self.line_new.text()
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT Password FROM AccountPassword WHERE Account=%s", (userID,))
                    res = cursor.fetchone()
                    if res and str(res[0]) == old_pwd:
                        cursor.execute("UPDATE AccountPassword SET Password=%s WHERE Account=%s", (new_pwd, userID))
                        conn.commit()
                        self.lbl_err.setText("Successfully Modify")
                    else:
                        self.lbl_err.setText("Original Password Error")
        except Exception as e:
            self.lbl_err.setText("Database Error")


# ================= 控制器代码 =================
class Controller:
    def __init__(self):
        self.current_window = None

    def _switch_win(self, new_win):
        """统一的窗口切换方法：安全关闭当前窗口，并显示新窗口"""
        if self.current_window:
            self.current_window.close()
        self.current_window = new_win
        self.current_window.show()

    # --- 1. 登录与主菜单路由 ---
    def show_login(self):
        self.login = Login_Ui()
        self.login.admin_window.connect(self.show_admin)
        self.login.teacher_window.connect(self.show_teacher)
        self.login.student_window.connect(self.show_student)
        self._switch_win(self.login)

    def show_admin(self):
        self._switch_win(Admin_Ui())
        self.current_window.query.connect(self.show_query)
        self.current_window.mi.connect(self.show_modify_info)
        self.current_window.cp.connect(self.show_change_password)
        self.current_window.logout.connect(self.back_login)

    def show_teacher(self):
        self._switch_win(Teacher_Ui())
        self.current_window.query.connect(self.show_query)
        self.current_window.sss.connect(self.show_set_student_score)
        self.current_window.cp.connect(self.show_change_password)
        self.current_window.lo.connect(self.back_login)

    def show_student(self):
        self._switch_win(Student_Ui())
        self.current_window.query.connect(self.show_query)
        self.current_window.change.connect(self.show_change_password)
        self.current_window.logout.connect(self.back_login)

    # --- 2. 公共功能模块 ---
    def show_change_password(self):
        self._switch_win(Change_Password_Ui())
        self.current_window.ret.connect(self.back_to_role_window)

    # --- 3. 查询子系统 (Query) ---
    def show_query(self):
        self._switch_win(Query_Ui())
        self.current_window.stu_info.connect(self.show_student_info_query)
        self.current_window.stu_score.connect(self.show_student_score_info_query)
        self.current_window.cou_info.connect(self.show_course_info_query)
        self.current_window.ti.connect(self.show_teacher_info_query)
        self.current_window.ave_score.connect(self.show_average_score_info_query)
        self.current_window.bs.connect(self.back_to_role_window)

    def show_student_info_query(self):
        self._switch_win(Student_Info_Query_Ui())
        self.current_window.back.connect(self.show_query)

    def show_student_score_info_query(self):
        self._switch_win(Student_Score_Query_Ui())
        self.current_window.back.connect(self.show_query)

    def show_course_info_query(self):
        self._switch_win(Course_Info_Query_Ui())
        self.current_window.back.connect(self.show_query)

    def show_teacher_info_query(self):
        self._switch_win(Teaching_Info_Query_Ui())
        self.current_window.back.connect(self.show_query)

    def show_average_score_info_query(self):
        self._switch_win(Average_Score_Info_Query_Ui())
        self.current_window.back.connect(self.show_query)

    # --- 4. 修改子系统 (Admin 专用) ---
    def show_modify_info(self):
        self._switch_win(Modify_Info_Ui())
        self.current_window.stu_info.connect(self.show_student_info_modify)
        self.current_window.cou_info.connect(self.show_course_info_modify)
        self.current_window.coc_info.connect(self.show_course_choosing_info_modify)
        self.current_window.bs.connect(self.back_to_role_window)

    def show_student_info_modify(self):
        self._switch_win(Student_Info_Modify_Ui())
        self.current_window.back.connect(self.show_modify_info)

    def show_course_info_modify(self):
        self._switch_win(Course_Info_Modify_Ui())
        self.current_window.back.connect(self.show_modify_info)

    def show_course_choosing_info_modify(self):
        self._switch_win(Course_Choosing_Info_Modify_Ui())
        self.current_window.back.connect(self.show_modify_info)

    # --- 5. 评分系统 (Teacher 专用) ---
    def show_set_student_score(self):
        self._switch_win(Set_Student_Score_Ui())
        self.current_window.back.connect(self.back_to_role_window)

    # --- 6. 全局导航控制 ---
    def back_to_role_window(self):
        global userChar
        if userChar == "admin":
            self.show_admin()
        elif userChar == "teacher":
            self.show_teacher()
        elif userChar == "student":
            self.show_student()

    def back_login(self):
        global userID, userChar
        userID, userChar = "", "" 
        self.show_login()


if __name__ == "__main__":
    # 自动体检：尝试读取账号表，失败则说明是新库，自动初始化
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM AccountPassword LIMIT 1")
    except Exception:
        print("检测到数据库表缺失，正在自动修复...")
        Initialize_Database()
    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QPushButton { min-height: 25px; border-radius: 4px; background-color: #f0f0f0; border: 1px solid #c0c0c0; } QPushButton:hover { background-color: #e0e0e0; }")
    
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec())