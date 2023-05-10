from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///st.sqlite3'
db = SQLAlchemy(app)

############ table for Subject ############
class Subject(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(20))

############ table for Teacher ############
class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(20))
    teacher_sub = db.Column(db.Integer, db.ForeignKey('subject.sub_id'))
    subject = db.relationship('Subject')

############ table for Student ############
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(20))
    rollNo = db.Column(db.String(20))
    subject_name = db.Column(db.String(20), db.ForeignKey('subject.sub_id'))
    teacher_name = db.Column(db.String(20), db.ForeignKey('teacher.teacher_id'))
    marks = db.Column(db.String(20))
    subject = db.relationship('Subject')
    teacher = db.relationship('Teacher')

############## function to add record in DB #############
@app.route("/", methods = ['POST', 'GET'])
def addStudentRecord():
    teacher_name = Teacher.query.all()
    all_sub_name = Subject.query.all()
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        subject = request.form['subject']
        teacher = request.form['teacher']
        marks = request.form['marks']
        check = Student.query.filter_by(student_name=name)
        for field in check:
            if field.student_name == name and field.rollNo == roll_no and field.subject_name != subject:        
                obj = Student(student_name=name, rollNo=roll_no, subject_name=subject, teacher_name=teacher, marks=marks)
                db.session.add(obj)
                db.session.commit()
                return redirect(url_for('listing'))
            else:
                flash("Student already in record, so please Enter valid details! (check Roll No. or subject)")
                return render_template('studentForm.html', all_sub_name=all_sub_name, teacher_name=teacher_name)
        if  name not in check:
                obj = Student(student_name=name, rollNo=roll_no, subject_name=subject, teacher_name=teacher, marks=marks)
                print("obj", obj)
                db.session.add(obj)
                db.session.commit()
                flash("Student details added Successfully!")
                return redirect(url_for('listing'))
    return render_template('studentForm.html', all_sub_name=all_sub_name, teacher_name=teacher_name)

############### to show all records ##################
@app.route('/list', methods=['POST', 'GET'])
def listing():
    if request.method == 'POST':
        name = request.form['name']
        obj = Student.query.filter_by(student_name=name)
        total = 0
        count = 0
        for mark in obj:
            total+= int(mark.marks)
            count += 1
        percentage = total/count
        all_student = Student.query.all()
        for std in all_student:
            std.subject_name = Subject.query.get(std.subject_name).sub_name
            std.teacher_name = Teacher.query.get(std.teacher_name).teacher_name
        return render_template('listing.html', all_student=all_student, total=total, name = name, percentage=percentage)
    all_student = Student.query.all()
    for std in all_student:
        std.subject_name = Subject.query.get(std.subject_name).sub_name
        std.teacher_name = Teacher.query.get(std.teacher_name).teacher_name
    return render_template('listing.html', all_student=all_student)

############### TO update the record ###############
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        teacher = request.form['teacher']
        marks = request.form['marks']
        obj = Student.query.get(id)
        obj.student_name = name
        obj.subject_name = subject
        obj.teacher_name = teacher
        obj.marks = marks
        db.session.commit()
        return redirect(url_for('listing'))
    matched_record = Student.query.get(id)
    matched_record.subject_name = Subject.query.get(matched_record.subject_name).sub_name
    matched_record.teacher_name = Teacher.query.get(matched_record.teacher_name).teacher_name
    teacher_name = Teacher.query.all()
    all_sub_name = Subject.query.all()
    return render_template('update.html', matched_record = matched_record, all_sub_name=all_sub_name, teacher_name=teacher_name)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    obj = Student.query.get(id)
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('listing'))


############# create all table in DB ###############
with app.app_context():
    db.create_all()