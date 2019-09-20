from flask import Flask, Response, request, jsonify, render_template, redirect, flash
from flask_pymongo import pymongo
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin
from database import DatabaseConnection
import datetime


app = Flask(__name__)
db = DatabaseConnection()
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'b247a64e246b8506f436afdd631d9ba07a95acf093b58a9af013944d92cebd92'
login_manager = LoginManager(app)


# Authentication
@login_manager.user_loader
def loadUser(userId): 
    return db.findOne("users", {"_id": userId})

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
            db.insert("users", document)
            flash(f'Your account has been created for {form.username.data}! You are now able to log in', 'success')
            return redirect("/properties") 
    return Response(render_template("Register.html", form = form), status=200, content_type = "text/html")

@app.route("/login/", methods = ["GET", "POST"])
def login(): 
     form = LoginForm()
     if form.validate_on_submit(): 
         user = db.findOne("users", {"email": form.email.data})
         if user and bcrypt.check_password_hash(user.password, form.password.data): 
             login_user(user, remember = form.remember.data)
             return redirect("/properties/")
        else: 
            flash("login unsuccessful. Please check email and password", "danger")
     return Response(render_template("Login.html", form=form), status = 200, content_type = "text/html")


@app.route("/properties/", methods=["GET"])
def getProperties(): 
    properties = db.findMany("properties", {"user": []})
    return render_template("properties.html", props=properties)

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

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=4000, debug=True)
