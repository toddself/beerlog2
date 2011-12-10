from flask import render_template, url_for, redirect, request, flash, session

from beerlog.comment.forms import EntryCommentForm

def add_comment(entry_id=-1):
    comment_form = EntryCommentForm()
    if comment_form.validate_on_submit():
        pass
    else:
        pass