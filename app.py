from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Users
@app.route('/users')
def users():

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM users")

    users = cur.fetchall()

    if result > 0:
        return render_template('users.html', users=users)
    else:
        msg = 'No Users Found'
        return render_template('users.html', msg=msg)

    cur.close()


#Single user
@app.route('/user/<string:id>/')
def user(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cur.fetchone()
    return render_template('user.html', user=user)



# home
@app.route('/home')
def home():

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")

    users = cur.fetchall()

    if result > 0:
        return render_template('home.html', users=users)
    else:
        msg = 'No Users Found'
        return render_template('home.html', msg=msg)
    cur.close()

# Users Form Class
class UserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add User
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        body = form.body.data

        cur = mysql.connection.cursor()
        session['logged_in']=True
        session['email'] = 'flaskhomework@mail.com'

        cur.execute("INSERT INTO users(username, body, email) VALUES(%s, %s, %s)" ,(username, body, session['email']))

        mysql.connection.commit()
        cur.close()
        flash('User Created', 'success')
        return redirect(url_for('home'))
    return render_template('add_user.html', form=form)


# Edit user
@app.route('/edit_user/<string:id>', methods=['GET', 'POST'])
def edit_user(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE id = %s", [id])

    user = cur.fetchone()
    cur.close()

    form = UserForm(request.form)
    form.username.data = user['username']
    form.body.data = user['body']

    if request.method == 'POST' and form.validate():
        username = request.form['username']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(username)
        cur.execute ("UPDATE users SET username=%s, body=%s WHERE id=%s",(username, body, id))
        mysql.connection.commit()
        cur.close()

        flash('User Updated', 'success')

        return redirect(url_for('home'))

    return render_template('edit_user.html', form=form)

# Delete user
@app.route('/delete_user/<string:id>', methods=['POST'])
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", [id])
    mysql.connection.commit()

    cur.close()

    flash('User Deleted', 'success')

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
