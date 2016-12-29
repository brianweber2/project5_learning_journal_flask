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

import forms
import models

app = Flask(__name__)
app.secret_key = 'dfja;dsklfj;34kjf0dcs$TGERWVSDVG'

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.template_filter()
def format_date(date):
    """Format datetime date in template."""
    return date.strftime('%B %d, %Y')


@app.route("/")
@app.route("/list")
def list_entries():
    """
    Contains a list of journal entries, which displays Title, Date for Entry.
    Title should be hyperlinked to the detail page for each journal entry.
    Include a link to add an entry.
    """
    entries = models.Entry.select()
    return render_template("index.html", entries=entries)


@app.route("/add", methods=['POST', 'GET'])
def add_entry():
    """
    Allows user to add journal entry with the following fields: Title, Date,
    Time Spent, What You Learned, Resources to Remember.
    """
    form = forms.AddEntryForm()
    if form.validate_on_submit():
        flash("New journal entry has been added!", "success")
        models.Entry.create(
            title=form.title.data,
            date=form.date.data,
            time=form.time.data,
            notes=form.notes.data,
            resources=form.resources.data
        )
        return redirect(url_for('list_entries'))
    return render_template("new.html", form=form)


@app.route("/edit/<int:entry_id>")
def edit_entry(entry_id):
    """
    Allows user to edit a journal entry with the following fields: Title, Date,
    Time Spent, What You Learned, Resources to Remember.
    """
    try:
        entry = models.Entry.select().where(models.Entry.id==entry_id).get()
    except models.Entry.DoesNotExist:
        abort(404)

    if request.method == 'POST':
        form = forms.EditEntryForm(request.form, obj=entry)
        if form.validate():
            form.populate_obj(entry)
            entry.save()
            flash("Entry has been updated!")
    else:
        form = forms.EditEntryForm(obj=entry)
    return render_template("edit.html", form=form, entry=entry)


@app.route("/details/<int:entry_id>")
def details(entry_id):
    """
    Create “details” view with the route “/details” displaying the journal
    entry with all fields: Title, Date, Time Spent, What You Learned,
    Resources to Remember. Include a link to edit the entry.
    """
    return render_template("detail.html")


@app.route("/delete/<int:entry_id>")
def delete_entry(entry_id):
    """Add the ability to delete a journal entry."""
    pass


if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT, host=HOST)
