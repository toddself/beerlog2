import hashlib
import os
from datetime import datetime, timedelta

from flask import render_template, url_for, redirect, request, flash, session
from sqlobject import AND, SQLObjectNotFound

from beerlog import app
from beerlog.blog.models import Entry, Tag
from beerlog.blog.forms import EntryForm
from beerlog.settings import *
from beerlog.admin.views import require_auth

@app.route('/')
@app.route('/entry/<entry_id>/')
@app.route('/entry/<year>/<month>/<day>/')
@app.route('/entry/<year>/<month>/<day>/<slug>/')
def list_entries(entry_id=None, day=None, month=None, year=None, slug=None):
    if entry_id:
        entries = Entry.select(AND(Entry.q.id == entry_id,
                                   Entry.q.deleted == False,
                                   Entry.q.draft == False))
    elif day and month and year:
        time_string = "%s-%s-%s" % (year, month, day)
        start_date = datetime.strptime(time_string, DATE_FORMAT)
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

@app.route('/entry/edit/', methods=['POST', 'GET'])
@app.route('/entry/edit/<entry_id>/', methods=['POST', 'GET'])
@require_auth
def edit_entry(entry_id=-1):
    post = EntryForm()
    if post.validate_on_submit():
        # valid call to post, lets make our post on time
        post_on = datetime.combine(post.date.data.date(), post.time.data.time())        
        try:
            # are we editing a post?
            entry = Entry.get(post.post_id.data)
        except SQLObjectNotFound:
            # not an edit -- no post found by the id presented
            entry = Entry(title=post.title.data,
                          body=post.body.data,
                          author=session.get('user_id'),
                          post_on=post_on,
                          draft=post.is_draft.data)
            if post.tags.data:
                [entry.addTag(Tag(name=t)) for t in post.tags.data.split(',')]
            flash("New entry <em>%s</em> was sucessfully added" % entry.title)
        else:
            entry.title = post.title.data
            entry.body = post.body.data
            entry.author = session.get('user_id')
            entry.post_on = post_on
            entry.last_modified = datetime.now()
            entry.draft = post.is_draft.data
            entry.deleted = post.is_deleted.data
            if post.tags.data:
                [entry.removeTag(t) for t in entry.tags]
                [entry.addTag(Tag(name=t)) for t in post.tags.data.split(',')]
            flash("<em>%s</em> was updated" % entry.title)
        return redirect(url_for('list_entries', entry_id=entry.id))
    else:
        try:
            entry = Entry.get(entry_id)
        except SQLObjectNotFound:
            entry = {'title': '',
                     'body': '',
                     'deleted': False,
                     'draft': False,
                     'id': 0}
            tags = ""
            date = datetime.now()
        else:
            date = entry.post_on
            tags = ','.join([t.name for t in entry.tags])
            
        return render_template('edit_entry.html',
                               data={'form': post, 
                                     'date': datetime.now(),
                                     'entry': entry,
                                     'tags': tags})

@app.route('/entry/edit/<entry_id>/delete/')
@require_auth
def delete_entry(entry_id=None):
    if not entry_id:
        flash("You have to specify a post to delete")
    else:
        entry = Entry.get(entry_id)
        entry.deleted = True
        flash("Entry <em>%s</em> has been marked as deleted. (This means it can \
               be recovered!)" % entry.title)
        return redirect(url_for('list_entries'))