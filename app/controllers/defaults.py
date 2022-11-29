from flask import Flask, render_template,request, redirect, url_for, session, jsonify, send_from_directory, flash, send_file
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from app import app
from app import allowed_file
from app import mysql
from datetime import date

data_atual = date.today()
data_em_texto = '{}/{}/{}'.format(data_atual.day, data_atual.month,data_atual.year)

UPLOAD_FOLDER_BOOK = 'C:\\Users\\Cliente\\Documents\\GitHub\\OmegaTCC\\app\\static\\arquivos\\Livros'
UPLOAD_FOLDER_WORK = 'C:\\Users\\Cliente\\Documents\\GitHub\\OmegaTCC\\app\\static\\arquivos\\Trabalhos'

username = ''
total_user = ''
nome = ""


i = 0

lista_book = []
lista_work = []

def etc(diretorio,file):
    path = diretorio
    dir = os.listdir(path)
    if file == "":
        pass
    elif file in dir:
        os.remove(f'{path}/{file}')


@app.route('/')
def index():
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global nome
    # Login do Administrador
    global username

    msg = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form: 
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM adm_accounts WHERE user_adm = % s And password_adm = MD5(%s)', (username, password))
        account = cursor.fetchone()
        if account:
            session['session_adm'] = True
            session['id'] = account['id'] 
            session['username'] = account['user_adm'] 
            msg = 'Logado com Sucesso!!'
            return redirect(url_for('index'))
        else: 
            if request.method == 'POST' and 'username' in request.form and 'password' in request.form: 
                username = request.form['username']
                password = request.form['password']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE username = % s And password = MD5(%s)', (username, password))
                account = cursor.fetchone()
                if account:
                    session['session_user'] = True
                    session['id'] = account['id'] 
                    session['nome'] = account['nome']
                    session['username'] = account['username'] 
                    msg = 'Logado com Sucesso!!'
                    return redirect(url_for('index'))
                else: 
                    msg = 'Usuário ou Senha Incorretos !!'
            
    return render_template('login.html', msg = msg) 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get("session_adm"):
        if session.get("session_user"):
            return redirect('404')
        return redirect("login")

    msg = '' 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'nome' in request.form and 'turma' in request.form and 'gender' in request.form: 
        username = request.form['username'] 
        password = request.form['password'] 
        email = request.form['email'] 
        nome = request.form['nome']   
        turma = request.form['turma'] 
        gender = request.form['gender']  
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, )) 
        account = cursor.fetchone() 
        if account: 
            msg = 'conta ja existe'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'email invalido'
        elif not re.match(r'[A-Za-z0-9]+', username): 
            msg = 'nome deve conter apenas caracteres e números!'
        else: 
            cursor.execute(f'INSERT INTO accounts (username, nome, password, turma, email, gender) VALUES ("{username}", "{nome}", MD5("{password}"),"{turma}", "{email}", "{gender}")')
            mysql.connection.commit() 
            msg = 'Cadastrador com sucesso!'
    elif request.method == 'POST': 
        msg = 'Por favor, preencha o formulário !'
    return render_template('register.html', msg = msg) 

@app.route('/logout') 
def logout(): 

   session.pop('session_adm', None)
   session.pop('session_user', None) 
   session.pop('nome', None)
   session.pop('id', None) 
   session.pop('username', None) 
   return redirect(url_for('index')) 

@app.route('/painel')
def painel():
    if not session.get("session_adm"):
        if session.get("session_user"):
            return redirect('404')
        return redirect("login")

    global total_user

    consulta_sql = "select * from accounts"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql)
    total_user = cursor.rowcount

    total_book = len(lista_book)
    total_work = len(lista_work)

    return render_template('painel.html', total_user=total_user, total_book=total_book, total_work=total_work)


@app.route('/users', methods=['GET', 'POST'])
def users():

    if not session.get("session_adm"):
        if session.get("session_user"):
            return redirect('404')
        return redirect("login")


    busca = ""

    if not session.get("session_adm"):
        return redirect("/login")
        
    if request.method == "POST":
        busca = request.form.get('busca')

    
    consulta_sql = "select * from accounts"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql)
    linhas = cursor.fetchall()
    

    
    
    return render_template('users.html', linhas=linhas, busca=busca)

@app.route('/upload_book')
def upload_book():
    return render_template('register_book.html')

@app.route('/upload_book2', methods=['GET', 'POST'])
def upload_book2():

    file = request.files['file']
    savepath = os.path.join(UPLOAD_FOLDER_BOOK, secure_filename(file.filename))
    file.save(savepath)            
   
    
    return render_template('register_book.html', lista_book=lista_book, data_atual=data_em_texto)
    

@app.route('/livros', methods=['GET', 'POST'])
def livros():
    busca = ""
    delete = ""
    linha = []

    if request.method == "POST":
        delete = request.form.get('delete')

    etc(UPLOAD_FOLDER_BOOK, delete)

    lista_book.clear()
    pasta = UPLOAD_FOLDER_BOOK
    for diretorio, subpastas, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            arq = (os.path.join(os.path.realpath(diretorio), arquivo))
            lista_book.append(arq)
    
    if request.method == "POST":
        busca = request.form.get('busca')



    return render_template('Livros.html', busca=busca, lista_book=lista_book)

@app.route('/upload_work')
def upload_work():
    return render_template('register_work.html')

@app.route('/upload_work2', methods=['GET', 'POST'])
def upload_work2():

    file = request.files['file']
    savepath = os.path.join(UPLOAD_FOLDER_WORK, secure_filename(file.filename))
    file.save(savepath)            
   
    
    return render_template('register_work.html', lista_work=lista_work)
    

@app.route('/Trabalhos', methods=['GET', 'POST'])
def work():
    busca = ""
    linha = []
    delete = ""
    
    if request.method == "POST":
        delete = request.form.get('delete')

    etc(UPLOAD_FOLDER_WORK, delete)
    

    lista_work.clear()
    pasta = UPLOAD_FOLDER_WORK
    for diretorio, subpastas, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            arq = (os.path.join(os.path.realpath(diretorio), arquivo))
            lista_work.append(arq)
    
    if request.method == "POST":
        busca = request.form.get('busca')
        

    return render_template('trabalhos.html', busca=busca, lista_work=lista_work)



@app.route('/get-file_b/<filename>')
def getfile_b(filename):
    file = os.path.join(UPLOAD_FOLDER_BOOK, filename)
    return send_file(file, mimetype='arq/pdf')

@app.route('/get-file_w/<filename>')
def getfile_w(filename):
    file = os.path.join(UPLOAD_FOLDER_WORK, filename)
    return send_file(file, mimetype='arq/pdf')




@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')