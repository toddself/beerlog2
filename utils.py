def authenticated():
    if not session.get('logged_in'):
        return redirect
