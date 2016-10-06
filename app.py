import os
import sqlite3
from flask import  Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)



app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('WHATDO_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('select title, text, timestamp, id from entries where name = ? order by id desc', [session.get('username')])
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    error = None
    if request.method == 'POST':
        db = get_db()
        if not request.form['username']:
            error = 'Please enter a username'
        elif not request.form['password']:
            error = 'You really need a password'
        elif db.execute("select name from users where name = ?", [request.form["username"]]).fetchall():
            error = "User already exists!!!"
        else:
            flash("You've created an account")
            db.execute("insert into users (name, password) values (?, ?)",
                       [request.form["username"], request.form["password"]])
            db.commit()
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text, name) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], session.get('username')])
    db.commit()
    flash('New entry was successfully eposted')
    return redirect(url_for('show_entries'))

@app.route('/remove', methods=['POST'])
def remove_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute("delete from entries where id = ?", [request.args.get("id", '')])
    db.commit()
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        if not request.form['username']:
            error = 'Username is required'
        elif not request.form['password']:
            error = 'Password is required'
        elif db.execute("select password from users where name = ?", [request.form['username']]).fetchall()[0][0] != request.form['password']:
            print db.execute("select password from users where name = ?", [request.form['username']]).fetchall()
            error = "Incorrect Password"
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
