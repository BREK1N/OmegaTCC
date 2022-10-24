from colorama import Cursor
from flask import Flask, render_template,request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app import app
from app import mysql

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login do Administrador
    msg = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form: 
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM adm_accounts WHERE user_adm = % s And password_adm = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['session_adm'] = True
            session['id'] = account['id'] 
            session['username'] = account['user_adm'] 
            msg = 'Logado com Sucesso!!'
            return render_template('index.html', msg = msg) 
        else: 
            msg = 'Usuário ou Senha Incorretos !!'
    return render_template('login.html', msg = msg) 

@app.route('/logout') 
def logout(): 
   session.pop('session_adm', None) 
   session.pop('id', None) 
   session.pop('username', None) 
   return redirect(url_for('index')) 

