from flask import Flask, Response, request, jsonify, render_template, redirect
from flask_pymongo import pymongo
from forms import RegistrationForm, LoginForm
from database import DatabaseConnection
import datetime


app = Flask(__name__)
db = DatabaseConnection()
app.config['SECRET_KEY'] = 'b247a64e246b8506f436afdd631d9ba07a95acf093b58a9af013944d92cebd92'


@app.route("/", methods=["GET"]) 
def helloWorld(): 
    # return one line of html, if we get to this response, return a 200 status code
    return Response(render_template("homePage.html"), status = 200, content_type="text/html")

@app.route("/register/", methods=["GET"]) 
def register(): 
    form = RegistrationForm()
         if form.validate_on_submit(): 
         document = {
             "username": form.username.data,
             "password": form.password.data, 
             "accountType": 
         }
    return Response(render_template("Register.html", form = form), status=200, content_type = "text/html")

@app.route("/login/", methods = ["GET", "POST"])
def login(): 
     form = LoginForm()
     return Response(render_template("Login.html", form=form), status = 200, content_type = "text/html")

@app.route("/addNewProperty/", methods = ["POST"])
def addNewProperty(): 
    document = {
        "name": request.form["name"], 
        "propertyType": request.form["type"], 
        "price": request.form["price"], 
        "image": request.form["image"]
    }
    db.insert("properties", document)
    return Response("Property succesfully added", status = 200, content_type="text/html")

@app.route("/properties/", methods=["GET"])
def getProperties(): 
    properties = db.findMany("properties", {})
    return render_template("properties.html", props=properties)

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=4000, debug=True)
