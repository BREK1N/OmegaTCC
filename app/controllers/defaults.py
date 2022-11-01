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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get("session_adm"):
        return redirect("login")

    msg = '' 
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'turma' in request.form and 'password' in request.form:
        firstname = request.form['firstname'] 
        lastname = request.form['lastname'] 
        email = request.form['email'] 
        password = request.form['password']   
        turma = request.form['turma'] 
        gender = request.form['gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM accounts WHERE firstname = % s', (firstname, )) 
        account = cursor.fetchone() 
        if account: 
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username): 
            msg = 'name must contain only characters and numbers !'
        else: 
            cursor.execute('INSERT INTO accounts VALUES (% s, % s, % s, % s, % s, % s,)', (firstname, lastname, password, turma, email, gender,)) 
            mysql.connection.commit() 
            msg = 'Registrador com sucesso'
    elif request.method == 'POST': 
        msg = 'Por favor, preencha o formulário !'
    return render_template('register.html', msg = msg) 

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

    consulta_sql = "select * from accounts"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql)
    linhas = cursor.fetchall()
    total_user = cursor.rowcount
    return render_template('painel.html', total_user=total_user)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')