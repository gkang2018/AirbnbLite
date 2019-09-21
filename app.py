from flask import Flask, Response, request, jsonify, render_template, redirect, flash, session
from flask_pymongo import pymongo
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, AnonymousUserMixin, login_required
from database import DatabaseConnection
import uuid
import datetime

app = Flask(__name__)
db = DatabaseConnection()
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'b247a64e246b8506f436afdd631d9ba07a95acf093b58a9af013944d92cebd92'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(UserMixin):

    def __init__(self, username, email, password, properties, accountType):

        self.username = username
        self.email = email
        self.password = password
        self.accountType = accountType
        self.properties = properties
        self._id = uuid.uuid4().hex

    def get_id(self):
        return self._id

    @classmethod
    def get_by_username(cls, username):
        data = db.findOne("users", {"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_email(cls, email):
        data = db.findOne("users", {"email": email})
        if data is not None:
            return cls(**data)
 
    @classmethod
    def get_by_id(cls, _id):
        data = db.findOne("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return bcrypt.check_password_hash(verify_user.password, password)
        return False

    @classmethod
    def register(cls, username, email, password, accountType, properties):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls( username, email, password, accountType, properties)
            session['email'] = email
            new_user.save_to_mongo()
            return True
        else:
            return False

    def json(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password, 
            "accountType": self.accountType, 
            "properties": self.properties, 
            "_id": self._id
        }

    def save_to_mongo(self):
        db.insert("users", self.json())

class Anonymous(User, AnonymousUserMixin):
  def __init__(self):
    self.lastname = 'Guest'

class AnonymousLogout(AnonymousUserMixin): 
    def __init__(self): 
        self.name = ""

@app.route("/", methods=["GET"]) 
def homePage(): 
    # return one line of html, if we get to this response, return a 200 status code
    return Response(render_template("homePage.html"), status = 200, content_type="text/html")

@app.route("/register/", methods=["GET", "POST"]) 
def register(): 
    form = RegistrationForm()
    # tells us if the registration was successfully validated 
    if form.validate_on_submit(): 
            # User authentication 
            hashedPassword = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            document = {
                "email": form.email.data, 
                "username": form.username.data,
                "password": hashedPassword, 
                "accountType": form.accountType.data, 
                "properties": []
             }  
            user = User.register(form.username.data, form.email.data, hashedPassword, [], form.accountType.data)
            flash(f'Your account has been created for {form.username.data}! You are now able to log in', 'success')
            return redirect("/") 
    return Response(render_template("Register.html", title = 'Register', form = form), status=200, content_type = "text/html")

@app.route("/login/", methods = ["GET", "POST"])
def login(): 
     form = LoginForm()
     if form.validate_on_submit(): 
         user = User.get_by_email(form.email.data)
         if User.login_valid(form.email.data, form.password.data): 
             login_user(user, remember = form.remember.data)
             login_manager.anonymous_user = Anonymous
             print(current_user.accountType)
             flash('You have been logged in!', 'success')
             return redirect("/properties")
         else: 
            flash(f'login unsuccessful. Please check email and password', "danger")
     return Response(render_template("Login.html", title = 'Login', form=form), status = 200, content_type = "text/html")


@app.route("/properties/", methods=["GET"])
@login_required
def getProperties(): 
    properties = db.findMany("properties", {"user": []})
    return render_template("properties.html", props=properties)

@app.route("/rentedProperties", methods = ["GET", "POST"])
def rentedProperties(): 
    if request.method == "POST": 
       propertyName = request.form.get("propertyName")
       propertyPrice = request.form.get("propertyPrice")
       property = db.findOne("properties", {"name": propertyName, "price": propertyPrice})
       property.user.append(current_user._id)
       current_user.properties.append(property._id)
    else: 
        
@app.route("/new/<id>", methods = ["GET"]) 
def newProperty(): 
    return render_template("newProperty.html")

@app.route("/addNewProperty/", methods = ["POST"])
def addNewProperty(): 
    document = {
        "name": request.form["name"], 
        "propertyType": request.form["propertyType"], 
        "price": request.form["price"], 
        "image": request.form["image"], 
        "user": []
    }
    db.insert("properties", document)
    return Response("Property succesfully added", status = 200, content_type="text/html")

@app.route("/logout/")
def logout():
    logout_user()
    login_manager.anonymous_user = AnonymousLogout
    return redirect("/")

# Authentication
@login_manager.user_loader
def loadUser(userId): 
    return User.get_by_id("userId")

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=4000, debug=True)


