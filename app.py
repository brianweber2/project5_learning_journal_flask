"""
Author: Brian Weber
Date Created: December 28, 2016
Revision: 1.0
Title: Learning Journal with Flask
Description: Create a local web interface of a learning journal. The main
(index) page will list journal entry titles with a title and date. Each
journal entry title will link to a detail page that displays the title, date,
time spent, what you learned, and resources to remember. Include the ability
to add or edit journal entries. When adding or editing a journal entry, there
must be prompts for title, date, time spent, what you learned, resources to
remember. The results for these entries must be stored in a database and
displayed in a blog style website. The HTML/CSS for this site has been
supplied for you.

For each part choose from the tools we have covered in the courses so far.
Please don’t employ more advanced tools we haven’t covered yet, even if they
are right for the job. However, if you identify a place where a more advanced
tool is appropriate, please mention that in a code comment as you and your
mentor may want to discuss it later.
"""
from flask import (Flask, g, render_template, flash, redirect, url_for,
                   request, abort)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from flask_bcrypt import check_password_hash

import forms
import models

import re
from unidecode import unidecode

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'dfja;dsklfj;34kjf0dcs$TGERWVSDVG'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


##### Template Filters #####

@app.template_filter()
def format_date(date):
    """Format datetime date in template."""
    return date.strftime('%B %d, %Y')


@app.template_filter()
def split_string(string, delimiter=','):
    """Split string in template by delimiter."""
    return string.strip().split(delimiter)


@app.template_filter()
def pluralize(number, singular='', plural='s'):
    """Pluralize word based on number in template."""
    if number == 1:
        return singular
    else:
        return plural


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return str(delim.join(result))


@app.template_filter('slugify')
def _slugify(string):
    """Slugify a string."""
    if not string:
        return ""
    else:
        return slugify(string)


@app.route("/")
def index():
    """
    If the user logs in: contains a list of journal entries, which displays
    Title, Date for Entry. Title should be hyperlinked to the detail page for
    each journal entry. Include a link to add an entry. If not: sent to
    welcome page.
    """
    if current_user in models.User.select():
        user = current_user
        journal = user.get_journal()
        return render_template('journal.html', journal=journal, user=user)
    else:
        return render_template('welcome.html')


@app.route('/tags/<string:tag>')
@login_required
def tags(tag):
    """Displays journal entries with a specific tag."""
    user = current_user
    journal = user.get_tagged_journals(tag)
    return render_template('journal.html', journal=journal, user=user, tag=tag)


@app.route("/add", methods=('POST', 'GET'))
@login_required
def add_entry():
    """
    Allows user to add journal entry with the following fields: Title, Date,
    Time Spent, What You Learned, Resources to Remember.
    """
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create_entry(
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learning=form.learning.data,
            resources=form.resources.data,
            user=g.user._get_current_object(),
            tags=form.tags.data
        )
        flash("New journal entry has been added!", "success")
        return redirect(url_for('index'))
    return render_template("new.html", form=form)


@app.route("/edit/<int:entry_id>", methods=('POST', 'GET'))
@login_required
def edit_entry(entry_id):
    """
    Allows user to edit a journal entry with the following fields: Title, Date,
    Time Spent, What You Learned, Resources to Remember.
    """
    try:
        entry = models.Entry.select().where(models.Entry.id==entry_id).get()
    except models.DoesNotExist:
        abort(404)
    else:
        form = forms.EntryForm(obj=entry)
        if request.method == 'POST':
            if form.validate_on_submit():
                if form.title.data != entry.title:
                    entry.slug = slugify(form.title.data)
                entry.user = g.user._get_current_object()
                entry.title = form.title.data
                entry.date = form.date.data
                entry.time_spent = form.time_spent.data
                entry.learning = form.learning.data
                entry.resources = form.resources.data
                entry.tags = form.tags.data
                entry.save()
                flash("Journal entry has been updated!", "success")
                return redirect(url_for('details', entry_id=entry.id, slug=entry.slug))
    return render_template("edit.html", form=form, entry=entry)


@app.route("/details/<int:entry_id>/<string:slug>")
def details(entry_id, slug):
    """
    Create “details” view with the route “/details” displaying the journal
    entry with all fields: Title, Date, Time Spent, What You Learned,
    Resources to Remember. Include a link to edit the entry.
    """
    try:
        entry = models.Entry.select().where(models.Entry.id==entry_id).get()
    except models.Entry.DoesNotExist:
        abort(404)
    return render_template("detail.html", entry=entry)


@app.route("/delete/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    """Add the ability to delete a journal entry."""
    try:
        entry = models.Entry.select().where(models.Entry.id==entry_id).get()
    except models.DoesNotExist:
        abort(404)
    else:
        entry.delete_instance()
        flash("Journal entry has been deleted!", "success")
    return redirect(url_for('index'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    """View for a new user to register."""
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        flash("Yay, you registered!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Login user."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    """Custom 404 error page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='brianweber2',
            email='brianweber2@gmail.com',
            password='surfer17',
            admin=True
        )
    except:
        print("User exists already.")
    app.run(debug=DEBUG, port=PORT, host=HOST)
