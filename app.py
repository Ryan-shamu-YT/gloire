import smtplib as smtp


from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import json
import os

import stripe


stripe_keys = {
    "publishable_key": "pk_test_51LaKO2HjwrYlW3BPnjo1ZClogfmkDYm02kaYHddSAmyfJ7VqOSFXbUfI4jc2WQUAEaiVOJkyzF5wymtFfguuBeWa00UJJyGLBh",
    "secret_key": "sk_test_51LaKO2HjwrYlW3BPuUB5eAR1be53TQaX0UyoHm9yQkMs1BDFgC16FtZf39FJ2ylgnM93Y7HtLukvkWcLOi65Lp5r00KcT8SjhN",
}

stripe.api_key = stripe_keys["secret_key"]

app = Flask(__name__)
app.secret_key = 'GloireBabies52598'


app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "gloirebabies"

mysql = MySQL(app)

@app.route('/success/')
def yes():
    return render_template("yes.html")


@app.route('/cancel/')
def no():
    return render_template("fail.html")

@app.route('/order/cart/')
def corder():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `cart` WHERE `owner` = %s ", (session['username'],))
    product = cursor.fetchall()

    table = []
    for obj in product:
        table.append({
                'price_data': {
                    'product_data': {
                        'name': obj['name'],
                    },
                    'unit_amount': obj['price'],
                    'currency': 'usd',
                },
                'quantity': 1,
            },)
    print(table)
    checkout_session = stripe.checkout.Session.create(
        line_items=table,
        phone_number_collection={
            'enabled': True,
        },
        payment_method_types=['card'],
        mode='payment',
        shipping_address_collection={
            'allowed_countries': ['ZW'],
        
        },
        success_url=request.host_url + '/success',
        cancel_url=request.host_url + '/cancel',
    )


    return redirect(checkout_session.url)


@app.route('/order/<product_id>')
def order(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `products` WHERE `id` = %s ", (product_id,))
    product = cursor.fetchone()
    print(product)
    price = product['price']
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price_data': {
                    'product_data': {
                        'name': product['name'],
                    },
                    'unit_amount': price,
                    'currency': 'usd',
                },
                'quantity': 1,
            },
        ],
        phone_number_collection={
            'enabled': True,
        },
        payment_method_types=['card'],
        mode='payment',
        shipping_address_collection={
            'allowed_countries': ['ZW'],
        },
        success_url=request.host_url + '/success',
        cancel_url=request.host_url + '/cancel',
    )


    return redirect(checkout_session.url)

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
        rprice = request.form['rprice']
        qq = request.form['qty']
        cursor.execute('SELECT * FROM `cart` WHERE `id` = %s AND `name` = %s AND `price` = %s AND `image` = %s AND `owner` = %s AND `rprice` = %s', (id, name, price, image, username, rprice))
        cartitem = cursor.fetchone()
        if cartitem:
            q = cartitem['q']
            newq = q + 1
            newp = cartitem['rprice'] + cartitem['price']
            cursor.execute('UPDATE `cart` SET `id`= %s,`name`= %s,`price`= %s,`image`= %s,`owner`= %s,`rprice`= %s, `q`= %s WHERE `id` = %s AND `name` = %s AND `price` = %s AND `image` = %s AND `owner` = %s AND rprice = %s;', (id, name, newp, image, username, rprice, newq, id, name, price, image, username, rprice))
        else: 
            cursor.execute('INSERT INTO `cart`(`id`, `name`, `price`, `rprice`, `image`, `owner`, `q`) VALUES(%s, %s, %s, %s, %s, %s, %s);', (id, name, price, rprice, image, username, qq))
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
    i = 0
    price = 0
    for obj in returndata:
        print(obj)
        i += obj['q']
        price += obj['rprice']
    return render_template('cart.html', data=returndata, amount=i, tprice=price)

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


@app.route('/callback', methods=['POST'])
def callback():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    endpoint_secret = 'whsec_XXX' # put Signing Secret here
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except (stripe.error.SignatureVerificationError,ValueError) as e:
        print(e)
        abort(400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        # save somewhere in database
        # that this session is completed
    return 'ok'

if __name__ == "__main__":
    app.run(debug=True)