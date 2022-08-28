from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re



app = Flask(__name__)
app.secret_key = 'GloireBabies52598'

app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "gloirebabies"

mysql = MySQL(app)



@app.route('/')
@app.route('/home/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM `news`')
    returndata = cursor.fetchall()
    return render_template('home.html', news=returndata)

@app.route('/profile/<id>')
def profile(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM `users` where id = %s', (id,))
    userc = cursor.fetchone()

    return render_template('profile.html', user=userc)



@app.route('/products/')
def products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM `products`')
    returndata = cursor.fetchall()
    return render_template('products.html', product=returndata)


@app.route('/add-to-cart', methods=['GET', 'POST'])
def add_to_cart():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        id = int(request.form['product_id'])
        name = request.form['product_name']
        price = request.form['product_price']
        image = request.form['product_image']
        username = session['username']
        cursor.execute('INSERT INTO `cart`(`id`, `name`, `price`, `image`, `owner`) VALUES(%s, %s, %s, %s, %s);', (id, name, price, image, username))
        mysql.connection.commit()

        return redirect(url_for('cart'))

@app.route('/remove-from-cart', methods=['GET', 'POST'])
def remove_from_cart():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        id = int(request.form['product_id'])
        name = request.form['product_name']
        price = request.form['product_price']
        image = request.form['product_image']
        username = session['username']
        cursor.execute('DELETE FROM `cart` WHERE `id`= %s AND `name` = %s AND `price` = %s AND `image` = %s AND `owner` = %s', (id, name, price, image, username))
        mysql.connection.commit()

        return redirect(url_for('cart'))

@app.route('/cart/')
def cart():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username = session['username']
    cursor.execute('SELECT * FROM `cart` WHERE `owner` = %s', (username,))
    returndata = cursor.fetchall()
    return render_template('cart.html', data=returndata)

@app.route('/search/' , methods=['GET', 'POST'])
def search():
    msg = ''
    id = ''
    dataa = ()
    if request.method == 'POST' and 'q' in request.form:
        id = request.form['q']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `products` WHERE (CONVERT(`name` USING utf8)) REGEXP %s LIMIT 0, 50;', (id,))
        dataa = cursor.fetchall()
        if dataa == ():
            msg = 'No Results Were Found'

    return render_template('search.html' , data=dataa, msg=msg, id=id)


@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    id = request.args.get('id')
    cursor.execute('SELECT * FROM `products` WHERE `id` = % s', (id,))
    data = cursor.fetchone()
    print(data)
    return render_template('checkout.html', dtaa=data)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['cart'] = []
            if account['username'] == 'Admin':
                session['admin'] = True
                msg = "Logged In Succesfully"
        else:
            msg =  "Account info is wrong or account does not exist"

    return render_template('login.html',msg=msg)

@app.route('/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('cart', None)
    # Redirect to login page
    return redirect(url_for('home'))


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    msg = ''
    username = ''
    password = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `users` WHERE `username` = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
             msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'

        cursor.execute('INSERT INTO `users`(`id`, `username`, `password`) VALUES( NULL, %s, %s);', (username, password))
        mysql.connection.commit()
        cursor.execute('SELECT * FROM `users` WHERE `username` = %s', (username,))
        account = cursor.fetchone()
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        session['cart'] = []
        msg = 'You have successfully signed up'
    return render_template('signup.html', msg=msg)  



app.run(debug=True)