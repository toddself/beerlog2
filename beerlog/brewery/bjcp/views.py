from flask import render_template

from beerlog import app
from beerlog.brewery.models import BJCPStyle, BJCPCategory

@app.route('/brewery/bjcp/')
def list_styles():
    bjcp_styles = {}
    for cat in list(BJCPCategory.select().orderBy('category_id')):
        styles_for_cat = list(BJCPStyle.select(BJCPStyle.q.category==cat).orderBy('subcategory'))
        try:
            bjcp_styles[cat.name]
        except KeyError:
            bjcp_styles[cat.name] = styles_for_cat
            

    return render_template('bjcp_browser.html', styles=bjcp_styles)