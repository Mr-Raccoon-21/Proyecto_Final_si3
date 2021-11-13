from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import speech_recognition as sr
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'si3.cqklnvxjex9m.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'UniversidadLatina123'
app.config['MYSQL_DB'] = 'si3'


# Intializacion de MySQL
mysql = MySQL(app)

print("=)")
#_________________________
#login
#_________________________
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to dashboard

            # _________________________

            return redirect(url_for('home'))








        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# _________________________
         #dashboard
# _________________________
@app.route('/dashboard')
def home():
    try:
        if session['loggedin'] == True:
            print("ok")
            return render_template('home.html')

    except:

        print("redirect ok")
        return redirect(url_for('login'))




#_________________________
          #logout
#_________________________

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


#_________________________
#registro
#_________________________


@app.route('/registro', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #validacion
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


#_________________________
#perfil
#_________________________
@app.route('/perfil')
def perfil():
    try:
        if session['loggedin'] == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            return render_template('perfil.html', account=account)



    except:

        return redirect(url_for('login'))






#_________________________
#transcripcionde texto
#_________________________
@app.route('/transcript', methods=["GET", "POST"])
def trans():
    try:
        if session['loggedin'] == True:
            transcript = ""
            user = session['username']

            try:

                if request.method == "POST":
                    print("audio recibido")

                    if "file" not in request.files:
                        return redirect(request.url)

                    file = request.files["file"]
                    fn = file.filename
                    if file.filename == "":
                        return redirect(request.url)

                    if file:
                        recognizer = sr.Recognizer()
                        audioFile = sr.AudioFile(file)
                        with audioFile as source:
                            data = recognizer.record(source)
                        transcript = recognizer.recognize_google(data, language='es-ES', key=None)

                        c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                        c.execute('INSERT INTO transcript  VALUES (NULL, %s, %s, %s)', (user, fn, transcript,))
                        # ('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                        mysql.connection.commit()

                        print("audio convertido a texto")
                        return redirect(url_for('home'))

            except:
                error = "formato de audio no soportado "

                return redirect(url_for('trans', error=error))

            return render_template('audio.html')


    except:

        print("redirect ok")
        return redirect(url_for('login'))




@app.route('/modulo_b')

def info():
    try:
        if session['loggedin'] == True:
            # --------
            # calculo de %
            porcentaje = 0
            # --------
            # SQl
            c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            c.execute('SELECT * FROM `transcript`')
            # cantidad de rows
            row = c.fetchall()

            # obtencion de contenido de las tablas
            e = []
            fn = []
            count = 0
            count_list = []
            content = {}
            content1 = {}
            content2 = {}
            for result in row:
                content = result['texto']  # valor de id
                content1 = result['file_name']  # valor de id

                fn.append(content1)

                count = 1 + count
                e.append(content)
            i = 0

            print("cantidad de lineas :", count)

            cpp = 0
            coo = 1
            p1 = 0
            p2 = 0
            # verificacion de exactitud y plabras repetidas
            cant1 = 0
            bnj = ""
            palabras = []
            palabras_r = []
            list = ""
            uii = count

            # _______

            lista_fn = []
            list_p = []
            list_por = []

            while cpp < count:
                print("inicio")
                # prorcentaje

                text = e[cpp]

                text = text.split()
                while coo < count:

                    ext = 0
                    text1 = e[coo]

                    v = 0
                    name = str(fn[cant1])
                    try:
                        name1 = str(fn[coo])
                        bnj = str(name + " y " + name1)
                        lista_fn.append(bnj)

                        text1 = text1.split()
                        print(porcentaje)
                        for val1 in text1:
                            p2 = p2 + 1

                            for val2 in text:
                                p1 = p1 + 1

                                if val2 == val1:
                                    # palabras

                                    # palabras repetidas
                                    list = list + val2 + " "
                                    palabras_r.append(val2)

                                    ext = 1 + ext

                        # ______

                        # __________

                        if p1 != 0 and p2 != 0:
                            v = int(p1 / p2)
                        if ext == 0:
                            list = " "

                        list_p.append(list)
                        list = " "

                        if v >= p2:
                            if ext != 0:

                                v_por = ((ext / v) * 100)

                                if v_por > 100:
                                    v_por = 100
                                p1 = 0
                                p2 = 0
                                porcentaje = v_por + porcentaje

                            else:
                                v_por = 0
                                porcentaje = porcentaje + 0
                                p2 = 0
                                p1 = 0


                        else:
                            if ext != 0:

                                v_por = ((ext / p2) * 100)
                                if v_por > 100:
                                    v_por = 100
                                porcentaje = v_por + porcentaje

                                p1 = 0
                                p2 = 0
                            else:
                                porcentaje = 0 + porcentaje
                                v_por = 0
                        v_por1 = str(v_por) + "%"
                        list_por.append(v_por1)
                        v_por = 0



                    except:
                        name1 = "error"

                    coo = coo + 1
                    print(list)

                # count

                cpp = 1 + cpp
                cant1 = 1 + cant1
                if coo == count:
                    coo = cpp + 1

            cant = 0
            # __
            # #_

            for item in palabras_r:
                if item not in palabras:
                    palabras.append(item)

            palabras = str(palabras)
            palabras = palabras.replace("[", " ")
            palabras = palabras.replace("'", " ")
            palabras = palabras.replace("]", " ")
            while (i != len(list_p)):
                count_list.append(i)
                i += 1

            if uii <= 2:
                cant = 1
            else:
                cant = uii
                if porcentaje != 0:
                    porcentaje = porcentaje / cant
                    if porcentaje > 100:
                        
                        porcentaje = 100
                    porcentaje = str(porcentaje)

                # candidad de palabras

                
            # obtencion de palabras

            return render_template('informe.html', porcentaje=porcentaje, count_list=count_list, list_p=list_p,
                                   lista_fn=lista_fn, list_por=list_por, palabras=palabras)



    except:

        print("redirect ok")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')







