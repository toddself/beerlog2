from __future__ import division
from __future__ import absolute_import
import hashlib
import os
from datetime import datetime

from werkzeug import secure_filename
from blog.models import Entry, Tag
from blog.forms import EntryForm

@app.route('/')
def show_entries():
    entries = Entry.select(Entry.q.draft==False).orderBy("-post_on")
    return render_template('show_entries.html', entries=entries)

@app.route('/upload', methods=['POST', 'GET'])
@require_auth
def upload_image():
    if request.method == 'POST':
        fn = request.files['file']
        if fn and allowed_file(fn.filename, app.config['ALLOWED_EXTENSIONS']):
            filename = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], 
                      secure_filename(fn.filename))
            try:
                os.stat(app.config['TEMP_UPLOAD_FOLDER'])
            except OSError:
                os.makedirs(app.config['TEMP_UPLOAD_FOLDER'])
            fn.save(filename)                      
            
            image, thumb = store_image(app.config, filename)
            
            return render_template('upload_file.html', 
                                    data={'thumb': thumb, 'img': image})
        else:
            flash("You either didn't supply a file or it wasn't a valid image")
            return render_template('upload_file.html')
    else:
        return render_template('upload_file.html')

@app.route('/add', methods=['POST', 'GET'])
@require_auth
def add_entry():
    post = PostForm(request.form)    
    if request.method == 'POST' and post.validate():
        entry = Entry(title=post.title.data,
                      body=post.post.data,
                      author=session.get('user_id'),
                      post_on=post.post_on.data)
        flash("New entry was sucessfully added")
        return redirect(url_for('show_entries'))
    else:
        return render_template('add_entry.html', 
                               data={'form': post, 'date': datetime.now()})


@app.route('/admin')
@require_auth
def admin():
    if not session.get('logged_in'):
        flash("You must be logged in")
        return redirect(url_for('add_entry'))
    else:
        pass
