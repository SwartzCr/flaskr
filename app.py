import os
import sqlite3
from flask import  Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Entry, Tag
from werkzeug.contrib.atom import AtomFeed
from forms import LoginForm, CommentSubmit, BaseForm, Remove
from wtforms import RadioField



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

@app.route('/', methods=['GET', 'POST'])
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    entries = db.query(Entry.title, Entry.text, Entry.timestamp, Entry.id, Entry.tag).filter(Entry.name==session.get('username')).order_by(Entry.id.desc())
    if request.args.get('tag',''):
        entries = entries.filter(Entry.tag==request.args.get('tag',''))
    entries = entries.all()
    tags = get_tags(db)
    tags = [(str(tag[0]),str(tag[0])) for tag in tags]
    form = CommentSubmit(meta={'csrf_context': session})
    form.tags.choices = tags
    remove = Remove(meta={'csrf_context': session})
    return render_template('show_entries.html', entries=entries, tags=tags, form=form, remove=remove)

def get_tags(db):
    tags = db.query(Tag.name).filter(Tag.username==session.get('username')).order_by(Tag.id.desc()).all()
    tags.append((u'Other',))
    return tags

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
            new_user = User(name=request.form["username"], password=request.form["password"], public=request.form["public"])
            db.add(new_user)
            db.commit()
            flash("You've created an account")
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    rform = CommentSubmit(request.form, meta={'csrf_context': session})
    rform.tags.choices = [(str(tag[0]),str(tag[0])) for tag in get_tags(db)]
    if not session.get('logged_in'):
        abort(401)
    if not rform.validate():
        abort(400)
    tag = ""
    if request.form['new_tag']:
        new_tag = Tag(name=request.form['new_tag'], username=session.get('username'))
        db.add(new_tag)
        db.commit()
        tag = request.form['new_tag']
    if request.form.get('tag'):
        tag = request.form['tag']
    new_entry = Entry(title=request.form['title'], text=request.form['text'], name=session.get('username'), tag=tag)
    db.add(new_entry)
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/remove', methods=['POST'])
def remove_entry():
    form = Remove(request.form, meta={'csrf_context': session})
    if not session.get('logged_in'):
        abort(401)
    if not form.validate():
        abort(400)
    db = get_db()
    db.delete(db.query(Entry).filter(Entry.id==request.args.get("id", '')).first())
    db.commit()
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('show_entries'))
    error = None
    if request.method == 'POST':
        rform = LoginForm(request.form, meta={'csrf_context': session})
        if not rform.validate():
            abort(400)
        db = get_db()
        if not request.form['username']:
            error = 'Username is required'
        elif not request.form['password']:
            error = 'Password is required'
        elif not db.query(User).filter(User.name==request.form["username"]).first():
            error = "Sorry there is no user with that name"
        elif db.query(User.password).filter(User.name==request.form["username"]).first()[0] != request.form['password']:
            error = "Incorrect Password"
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    db = get_db()
    public_users = db.query(User.name).filter(User.public==1).all()
    public_users = [user[0] for user in public_users]
    entries = db.query(Entry.title, Entry.text, Entry.timestamp, Entry.id).filter(Entry.name.in_(public_users)).order_by(Entry.id.desc()).all()
    form = LoginForm(meta={'csrf_context': session})
    return render_template('login.html', error=error, entries=entries, form=form, meta={'csrf_context': request.session})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/<user>/feed.atom')
def jam_feed(user):
    feed = AtomFeed('jams', feed_url=request.url, url=request.url_root)
    db = get_db()
    user_exists = db.query(User.name).filter(User.name==user).all()
    if not user_exists:
        abort(404)
    jams = db.query(Entry.title, Entry.text, Entry.name, Entry.tag, Entry.timestamp).filter(Entry.name==user).filter(Entry.tag=="jam").order_by(Entry.id.desc()).limit(2).all()
    for jam in jams:
        feed.add(jam.title,
                content_type='html',
                url=jam.text,
                author=jam.name,
                updated=jam.timestamp)
    return feed.get_response()
