import os
import sqlite3
from flask import  Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Entry

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key'))

def connect_db():
    """Connects to the specific database."""
    engine = create_engine('sqlite:///app.db', echo=True)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

#def init_db():
#    db = get_db()
#    with app.open_resource('schema.sql', mode='r') as f:
#        db.cursor().executescript(f.read())
#    db.commit()
#
#@app.cli.command('initdb')
#def initdb_command():
#    """Initializes the database."""
#    init_db()
#    print 'Initialized the database.'

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
    entries = db.query(Entry.title, Entry.text, Entry.timestamp, Entry.id).filter(Entry.name==session.get('username')).all()
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
        elif db.query(User).filter(User.name==request.form["username"]).all():
            error = "User already exists!!!"
        else:
            new_user = User(name=request.form["username"], password=request.form["password"])
            db.add(new_user)
            db.commit()
            flash("You've created an account")
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    new_entry = Entry(title=request.form['title'], text=request.form['text'], name=session.get('username'))
    db.add(new_entry)
    db.commit()
    flash('New entry was successfully eposted')
    return redirect(url_for('show_entries'))

@app.route('/remove', methods=['POST'])
def remove_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.delete(db.query(Entry).filter(Entry.id==[request.args.get("id", '')]).first())
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
        #TODO check to make sure user exists otherwise we error
        elif not db.query(User).filter(User.name==request.form["username"]).first():
            error = "Sorry there is no user with that name"
        elif db.query(User.password).filter(User.name==request.form["username"]).first()[0] != request.form['password']:
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
