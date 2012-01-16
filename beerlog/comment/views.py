from flask import render_template, url_for, redirect, request, flash, session

from beerlog.comment.models import Comment
from beerlog.comment.forms import EntryCommentForm

def add_comment(object_id, object_type):
    comment_form = EntryCommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(
            body = comment_form.body.data,
            posted_by_name = comment_form.posted_by_name.data,
            posted_by_email = comment_form.posted_by_email.data,
            ip_address = request.remote_addr,
            comment_object = int(object_id),
            comment_type = object_type)
        return_to = comment_form.return_to.data
        flash("Comment added")
        return redirect('%s' % return_to)
    else:
        return redirect(request.headers['referer'])