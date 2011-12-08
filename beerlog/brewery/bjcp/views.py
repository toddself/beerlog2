import json
from decimal import Decimal

from flask import render_template
from sqlobject import SQLObjectNotFound

from beerlog import app
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
        s = BJCPStyle.get(style_id)
        style = {
            'name': "%s. %s" % (s.subcategory, s.name),
            'beer_type': s.beer_type,
            'category': "%s. %s" % (s.category.id, s.category.name),
            'aroma': s.aroma,
            'appearance': s.appearance,
            'flavor': s.flavor,
            'mouthfeel': s.mouthfeel,
            'impression': s.impression,
            'comments': s.comments,
            'examples': s.examples,
            'og_range': s.og_range,
            'fg_range': s.fg_range,
            'ibu_range': s.ibu_range,
            'srm_range': s.srm_range,
            'abv_range': s.abv_range
            }
    except (SQLObjectNotFound, ValueError):
        style = {'error': 'There is no style for id %s' % style_id}
        
    return json.dumps(style)
    