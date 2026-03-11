from flask import Flask, request, current_app

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"