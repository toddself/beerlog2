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