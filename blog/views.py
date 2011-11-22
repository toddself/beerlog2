from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime, timedelta

from flask import render_template, url_for, redirect, request, flash, session
from werkzeug import secure_filename
from sqlobject import AND, SQLObjectNotFound

from blog.models import Entry, Tag
from blog.forms import EntryForm
from settings import TIME_FORMAT

def get_entry(entry_id=None, day=None, month=None, year=None, slug=None):
    if entry_id:
        entries = Entry.select(AND(Entry.q.id == entry_id,
                                   Entry.q.deleted == False,
                                   Entry.q.draft == False))
    elif day and month and year:
        time_string = "%s-%s-%s 00:00" % (year, month, day)
        start_date = datetime.strptime(time_string, TIME_FORMAT)
        end_date = start_date + timedelta(days=1)
        if slug:
            entries = Entry.select(AND(Entry.q.draft == False,
                                        Entry.q.slug == slug,
                                        Entry.q.deleted == False,
                                        AND(Entry.q.post_on > start_date,
                                            Entry.q.post_on < end_date)))
        else:
            entries = Entry.select(AND(Entry.q.draft == False,
                                       Entry.q.deleted == False,
                                       AND(Entry.q.post_on > start_date,
                                           Entry.q.post_on < end_date))
                                   ).orderBy("-post_on")
    else:
        entries = Entry.select(AND(Entry.q.draft == False,
                                   Entry.q.deleted == False)
                               ).orderBy("-post_on")

    return render_template('show_entries.html', entries=entries)

def edit_entry(entry_id=-1):
    post = EntryForm(request.form)
    if request.method == 'POST' and post.validate():
        try:
            entry = Entry.get(entry_id)
        except SQLObjectNotFound:
            entry = Entry(title=post.title.data,
                          body=post.post.data,
                          author=session.get('user_id'),
                          post_on=post.post_on.data,
                          draft=post.is_draft.data)
            flash("New entry <em>%s</em> was sucessfully added" % entry.title)
        else:
            entry.title = post.title.data
            entry.body = post.post.data
            entry.author = session.get('user_id')
            entry.post_on = post.post_on.data
            entry.last_modified = datetime.now()
            entry.draft = post.is_draft.data
            entry.deleted = post.is_deleted.data
            flash("<em>%s</em> was updated" % entry.title)
        return redirect(url_for('get_entry', entry_id=entry.id))
    else:
        try:
            entry = Entry.get(entry_id)
        except SQLObjectNotFound:
            pass
            
        return render_template('edit_entry.html',
                               data={'form': post, 'date': datetime.now()})

def delete_entry(entry_id=None):
    if not entry_id:
        flash("You have to specify a post to delete")
    else:
        entry = Entry.get(entry_id)
        entry.deleted = True
        flash("Entry %s has been marked as deleted. (This means it can \
               be recovered!)")
        return redirect(url_for('get_entry'))