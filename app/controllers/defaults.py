from flask import Flask, render_template,request, redirect, url_for, session
from app import app

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')