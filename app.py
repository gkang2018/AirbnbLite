from flask import Flask, Response, request, jsonify, render_template
from flask_pymongo import pymongo
from database import DatabaseConnection
import datetime

app = Flask(__name__)
db = DatabaseConnection()

@app.route("/", methods=["GET"]) 
def helloWorld(): 
    # return one line of html, if we get to this response, return a 200 status code
    return Response(render_template("homePage.html"), status = 200, content_type="text/html")

@app.route("/register/", methods=["GET"]) 
def register(): 
    return Response(render_template("Register.html"), status=200, content_type = "text/html")
@app.route("/")
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
    properties = db.findMany("properties", {

    })
    props = jsonify(properties)
    return props


if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=4000, debug=True)
