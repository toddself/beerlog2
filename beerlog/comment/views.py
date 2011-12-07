from flask import render_template, url_for, redirect, request, flash, session

from beerlog import app
from beerlog.comment.forms import EntryCommentForm

@app.route("/entry/<entry_id>/comment/add/")
def add_comment(entry_id=-1):
    comment_form = EntryCommentForm()
    if comment_form.validate_on_submit():
        pass
    else:
        pass