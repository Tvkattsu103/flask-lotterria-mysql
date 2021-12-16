from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.urls import url_parse

class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Login")
    recaptcha = RecaptchaField()

app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeckacdAAAAAHSQu1A2h2ZXnXSrcoAFwIOvyi3d'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeckacdAAAAADOPi7qaBle16terydNyysELh9E1'

# SqlAlchemy Database Configuration With Mysql
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:""@localhost/qlloterria"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'


#Creating model table for our CRUD database
class Data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))

class Food(db.Model):
    foodid = db.Column(db.Integer, primary_key=True)
    foodname = db.Column(db.String(100))
    price = db.Column(db.String(100))
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))
    category = db.Column(db.String(100))

    def __init__(self, foodname, price, description, image, category):

        self.foodname = foodname
        self.price = price
        self.description = description
        self.image = image
        self.category = category

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.Integer)
    
    def get_id(self):
        return self.id
    def is_active(self):
        return True
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

@login.user_loader
def load_user(role):
    return User.query.get(int(role))

@app.route("/")
@app.route("/index")
def Index():
    data = Food.query.all()
    return render_template("index.html", data =data)

@app.route("/menu")
def menu():
    data = Food.query.all()
    return render_template("menu.html", data =data)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/index')

    form = LoginForm()
    if form.validate_on_submit():
        # Kiem tra user co trong db hay khong
        # Thong tin user lay tu form: form.username.data
        user = User.query.filter_by(username=form.username.data).first()
        # user khong ton tai
        if user is not None:
            #Kiem tra password co khop không 
            password_ok = user.password == form.password.data
        if user is None or not password_ok:
            flash('Invalid username or password')
            return redirect('/login')
        
        flash('Login of user {}'.format(form.username.data))
        #su dung flask_login (login_user)
        login_user(user)
        # Xu ly next
        next_page = request.args.get('next')
        if next_page is not None:
            flash('Next page {}'.format(next_page))
            if url_parse(next_page).netloc != '':
                flash('netloc: ' + url_parse(next_page).netloc)
                next_page = '/index'
        else:
            next_page = '/index'
        return redirect(next_page)
    return render_template('login.html', form = form )

@app.route("/insert", methods=["POST"])
def insert():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        my_data = Data(name, email, phone)
        db.session.add(my_data)
        db.session.commit()

        flash("Employee Inserted Successfully")

        return redirect(url_for("Index"))


@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        my_data = Data.query.get(request.form.get("id"))

        my_data.name = request.form["name"]
        my_data.email = request.form["email"]
        my_data.phone = request.form["phone"]

        db.session.commit()
        flash("Employee Updated Successfully")

        return redirect(url_for("Index"))


@app.route("/delete/<id>/", methods=["GET", "POST"])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Employee Deleted Successfully")

    return redirect(url_for("Index"))


if __name__ == "__main__":
    app.run(debug=True)
