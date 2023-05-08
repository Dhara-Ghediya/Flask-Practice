from flask import Flask, render_template, request, redirect, url_for, session, flash    
# Flask-Dance provides a simple and easy-to-use way to add OAuth authentication to Flask apps.
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.contrib.google import make_google_blueprint, google
# install SQLAlchemy and import
from flask_sqlalchemy import SQLAlchemy
# install flask-mail to use mail protocol
from flask_mail import Mail, Message
from random import randint
import os

# configuration for database
app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('SESSION_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)

# configuration for Google Authentication
# app.config['SECRET_KEY'] = os.getenv("GOOGLE_SECRET_ID")
# app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
# app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv("GOOGLE_SECRET_ID")

# configuration for Flask-Mail protocol
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
mail = Mail(app)
otp = str(randint(000000,999999))

# model to create table in DB
class RegisterUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(20))
    mobile = db.Column(db.String(10))

# for home page ******************
@app.route('/home')
def home():
    if 'login' in session.keys():
        return render_template('home.html')
    return redirect(url_for('login'))

# for login user **************
@app.route('/simple-login/', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        email = request.form['email']
        psw = request.form['password']
        session['login'] = email
        login = RegisterUser.query.filter_by(email= email, password= psw).first()
        if login is not None:
            return redirect(url_for('home'))
    return render_template('login.html')

# for register user *****************
@app.route('/', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        uname = request.form['uname']
        email = request.form['email']
        password = request.form['password']
        phone_no = request.form['phone_no']
        obj = RegisterUser.query.filter_by(email= email).first()
        if obj == None:
            rgstr = RegisterUser(username = uname, email= email, password= password, mobile= phone_no)
            db.session.add(rgstr)
            db.session.commit()
            flash("Regiter Successfully!")
            return redirect(url_for("login"))
        else:
            error = 'Your mail id is already registered! Please register with new mail id.'
            return redirect(url_for("login"))
    return render_template('register.html', error = error)

# for change password *************
@app.route('/change-psw', methods=['POST', 'GET'])
def changePass():
    if request.method == 'POST':
        mail = request.form['email']
        oldPass = request.form['oldPass']
        newPass = request.form['newPass']
        confirmPass = request.form['confirmPass']
        
        # changePass = RegisterUser.query.filter_by(email= mail, password= oldPass).first() #.all()
        # SELECT register_user.id AS register_user_id, register_user.username AS register_user_username, register_user.email AS register_user_email, register_user.password AS register_user_password, register_user.mobile AS register_user_mobile
        print(changePass)
        # xyz = RegisterUser.query.get(10) # give --> <RegisterUser 10>
        if changePass is not None:
            if newPass == confirmPass:
                changePass.password = newPass
                # print("change",changePass.password)
                # print("new",newPass)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template('changePass.html')

# for send email to user for change forgot password link ***********
@app.route('/forgot-password', methods=['POST', 'GET'])
def forgotPass():
    if request.method == 'POST':
        email = request.form['email']
        session['forgot'] = email
        forgot = RegisterUser.query.filter_by(email= email).first()
        if forgot is not None:
            msg = Message()
            msg.subject = "Forgot Password Link"
            msg.recipients = [email]
            msg.sender = 'dghediya6602@gmail.com'
            msg.body = 'click on below link to change your forgotten password!'
            msg.html = '''<form action='http://127.0.0.1:5000//new-password' method="POST">
            <input type="hidden" value="''' + email + '''" name= "mailid">
            <button type="submit">Click Me!!!</button></form> '''
            mail.send(msg)
            return redirect(url_for('login'))
    return render_template('forgetPass.html')

@app.route('/new-password', methods=['POST'])
def newpsw():
    if request.method == 'POST':
        try:
            try:
                mailID = request.form['mailid']
            except:
                mailID = session['email']
                print("****", mailID)
            newPass = request.form['newPass']
            confirmPass = request.form['confirmPass']
            print("****", mailID)
            obj = RegisterUser.query.filter_by(email= mailID).first()
            if obj != None:
                if newPass == confirmPass:
                    print(obj)
                    obj.password = newPass
                    db.session.commit()
                    return redirect(url_for('login'))
            return render_template('newPass.html',mail=mailID)
        except:
            mailID=request.form['mailid']
            return render_template('newPass.html',mail=mailID)

# forgot password by otp
@app.route('/fotgot-pass-by-otp', methods=['POST', 'GET'])
def forgot_pass_by_otp():
    if request.method == 'POST':
        mail1= request.form['email']
        print("123", mail1)
        msg = Message()
        msg.subject = "one-Time Password"
        msg.recipients = [mail1]
        msg.sender = 'dghediya6602@gmail.com'
        msg.body = otp
        mail.send(msg)
        session['email'] = mail1
        # print(session['email'])
        return redirect(url_for('verify'))
    return render_template('byotp.html')

@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == 'POST':
        user_otp =  request.form['otp']
        print("otp", user_otp)
        # mail = session['email']
        if otp == int(user_otp):
            return redirect(url_for('newpsw'))
    return render_template('verify.html')

# for logout user **************
@app.route('/logout')
def logout():
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
if __name__ == '__main__':

    app.run(debug=True)
# else:
#     print("hello")










