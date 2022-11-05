from flask import Flask, render_template,request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename
from flask import send_from_directory, jsonify
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

UPLOAD_FOLDER_BOOK = 'C:\\Users\\Lucas\\Documents\\GitHub\\OmegaTCC\\app\\arquivos\\Livros'
UPLOAD_FOLDER_WORK = 'C:\\Users\\Lucas\\Documents\\GitHub\\OmegaTCC\\app\\arquivos\\Trabalhos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docs'}

username = ''
total_user = ''
total_book = ''
total_work = ''
nome = ""

lista_book = []


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

    consulta_sql_book = "select * from livros"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql_book)
    total_book = cursor.rowcount

    return render_template('painel.html', total_user=total_user, total_book=total_book)


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

@app.route('/upload_book', methods=['GET', 'POST'])
def upload_book():


    
    global arq
    global lista_book
    last_book = ""


    pasta = UPLOAD_FOLDER_BOOK
    for diretorio, subpastas, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            arq = (os.path.join(os.path.realpath(diretorio), arquivo))
            lista_book.append(arq)


    

    if request.method == 'POST':
        # verifique se a solicitacao de postagem tem a parte do arquivo
        if 'file' not in request.files:
            flash('Nao tem a parte do arquivo')
            return redirect(request.url)
        file = request.files['file']
        

        # Se o usuario nao selecionar um arquivo, o navegador envia um
        # arquivo vazio sem um nome de arquivo.
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if request.method == "POST":
                nome_livro = request.form.get('nome_book')
                isbn = request.form.get('ISBN')
                genero1 = request.form.get('genero1')
                genero2 = request.form.get('genero2')
                genero3 = request.form.get('genero3')
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
                cursor.execute('SELECT * FROM livros WHERE ISBN = % s', (isbn, )) 
                livro = cursor.fetchone() 
                cursor.execute(f'INSERT INTO livros (nome_livro, path, data, ISBN, genero_1,genero_2,genero_3) VALUES ("{nome_livro}", "{lista_book[::-1]}", "{data_em_texto}","{isbn}","{genero1}","{genero2}","{genero3}")')
                mysql.connection.commit()


            return redirect(url_for('upload_book'))


            
   
    
    return render_template('register_book.html', lista_book=lista_book, data_atual=data_em_texto)
    

@app.route('/livros', methods=['GET', 'POST'])
def livros():
    busca = ""
    linha = []

    lista_book.clear()
    pasta = UPLOAD_FOLDER_BOOK
    for diretorio, subpastas, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            arq = (os.path.join(os.path.realpath(diretorio), arquivo))
            lista_book.append(arq)
    
    if request.method == "POST":
        busca = request.form.get('busca')

    consulta_sql = "select * from livros"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(consulta_sql)
    linhas = cursor.fetchall()

    return render_template('Livros.html', linhas=linhas, busca=busca, lista_book=lista_book)



@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')