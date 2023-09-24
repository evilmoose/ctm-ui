from flask import Flask, render_template, redirect, session, jsonify

app = Flask(__name__)

app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

if __name__ == '__main__':
    app.run(debug=True)