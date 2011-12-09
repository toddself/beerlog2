import json

from flask import render_template
from sqlobject import SQLObjectNotFound

from beerlog import app, sqlobject_to_dict
from beerlog.brewery.models import BJCPStyle, BJCPCategory

@app.route('/brewery/bjcp/')
def list_styles():
    bjcp_styles = {}
    for cat in list(BJCPCategory.select().orderBy('category_id')):
        styles_for_cat = list(BJCPStyle.select(BJCPStyle.q.category==cat).orderBy('subcategory'))
        try:
            bjcp_styles[cat.category_id]
        except KeyError:
            bjcp_styles[cat.category_id] = {'name': cat.name, 'styles': styles_for_cat}

    return render_template('bjcp_browser.html', styles=bjcp_styles)
    
@app.route('/json/brewery/bjcp/style/<style_id>/')
def get_style_json(style_id=-1):
    try:
        style = sqlobject_to_dict(BJCPStyle.get(style_id))
    except SQLObjectNotFound:
        style = {'error': 'There is no style for id %s' % style_id}
        
    return json.dumps(style)
    