from flask import Flask, render_template,request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app import app
from app import mysql

username = ''
total_user = ''

@app.route('/')
def index():
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login do Administrador
    global username
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
            return redirect(url_for('index'))
        else: 
            msg = 'Usuário ou Senha Incorretos !!'
    return render_template('login.html', msg = msg) 

@app.route('/logout') 
def logout(): 
   session.pop('session_adm', None) 
   session.pop('id', None) 
   session.pop('username', None) 
   return redirect(url_for('index')) 


@app.route('/painel')
def painel():
    if not session.get("session_adm"):
        return redirect("/login")
    global total_user

    consulta_sql = "select * from adm_accounts"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql)
    linhas = cursor.fetchall()
    total_user = cursor.rowcount
    return render_template('painel.html', total_user=total_user)