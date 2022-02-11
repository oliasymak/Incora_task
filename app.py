from flask import Flask, render_template, jsonify, make_response
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
import jwt
from functools import wraps
from  werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '123456789'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:240702@localhost:5432/incora_users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class UsersList(db.Model):
    __table__name = 'users_list'
    id = db.Column('id', db.Integer, primary_key = True)
    first_name = db.Column('first_name', db.String(40))
    last_name = db.Column('last_name', db.String(40))
    email = db.Column('email', db.String(30))
    phone = db.Column('phone', db.String(10))
    password = db.Column('password', db.String(10))

    def __init__(self, id, first_name, last_name, email, phone, password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password = password

def fill_database():

    db.drop_all()
    db.create_all()
    user1 = UsersList(1, 'Ірина', 'Дмитрасевич', 'irynkadmytr@gmail.com', '0976783123', 'ira123')
    user2 = UsersList(2, 'Дмитро', 'Гнатенко', 'dhnatenko@gmail.com', '0730555123', '000000')


    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()


fill_database()




@app.route('/')
def index():
    return render_template("registration.html")

@app.route('/users', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        first_name = request.form.get('user_fname').strip()
        last_name = request.form.get('user_lname').strip()
        email = request.form.get('user_email').strip()
        phone = request.form.get('user_phone').strip()
        password = request.form.get('user_password')
    count_rows = db.session.query(UsersList).count()
    user = UsersList(count_rows+1, first_name, last_name, email, phone, password)
    if first_name == '' or last_name == '' or phone == '' or email == '' or password == '':
        return render_template("registration_not_complete.html")
    if first_name.isdigit() or last_name.isdigit():
        return render_template("registration_not_complete.html")
    if len(phone) !=10:
        return render_template("registration_not_complete.html")
    db.session.add(user)
    db.session.commit()
    rows = UsersList.query.all()
    return render_template("regastration_complete.html", rows=rows)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

@app.route('/loginned', methods=["GET", "POST"])
def loggined():
    auth = request.form

    if not auth or not auth.get('user_email') or not auth.get('user_password'):

        return make_response(
            'Could not verify!',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = UsersList.query \
        .filter_by(email=auth.get('user_email')) \
        .first()
    print(user)
    if not user:

        return make_response(
            'Could not verify&',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )


    if check_password_hash(user.password, auth.get('user_password')):
        # generates the JWT Token
        #token = jwt.encode({
            #'id': user.id,
            #'exp': datetime.utcnow() + timedelta(minutes=30)
        #}, app.config['SECRET_KEY'])

        #return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
        return render_template("login.html")
    # returns 403 if password is wrong
    else:
        return make_response(
            'Could not verify8',
            403,
            {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
        )

@app.route('/search_id', methods=["GET", "POST"])
def search_id():
    user = ""
    if request.method == "GET":
        return render_template("search_id.html", user = user)

@app.route('/result_id', methods=["GET", "POST"])
def result_id():
    if request.method == "POST":
        user_id = request.form.get('user_id').strip()
    if not user_id.isdigit():
        return render_template("search_not_complete.html")
    if UsersList.query.get(user_id) == None:
        return render_template("search_not_complete.html")
    row = UsersList.query.filter(UsersList.id == int(user_id))
    user = row[0].first_name + " " + row[0].last_name + " " + row[0].email + " " + row[0].password + " " + row[0].phone
    print(user)
    return render_template("search_id.html", user=user)

@app.route('/update', methods=["GET", "POST"])
def update():
    if request.method == "GET":
        return render_template("update.html")

@app.route('/updated', methods=["GET", "POST"])
def updated():
    if request.method == "POST":
        user_id = request.form.get('user_id').strip()
        first_name = request.form.get('user_fname').strip()
        last_name = request.form.get('user_lname').strip()
        email = request.form.get('user_email').strip()
        phone = request.form.get('user_phone').strip()
        password = request.form.get('user_password')

    UsersList.query.filter_by(id=user_id).update(
        dict(first_name=first_name, last_name=last_name, email=email, phone=phone, password=password))
    return render_template("udated.html")

if __name__ == "__main__":
    app.run()
