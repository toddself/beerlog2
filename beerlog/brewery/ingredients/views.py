import json

from flask import render_template, flash, url_for

from beerlog.brewery.models import *
from beerlog.helpers import sqlobject_to_dict

def list_ingredients(ingredient):
    c = {'hop': ['Hop',],
                  'grain': ['Grain',],
                  'extract': ['Extract',],
                  'hoppedextract': ['HoppedExtract'],
                  'mineral': ['Mineral',],
                  'herb': ['Herb',],
                  'spice': ['Spice',],
                  'flavor': ['Flavor',],
                  'fining': ['Fining',],
                  'yeast': ['Yeast',],}
    c['misc'] = c['mineral']+c['herb']+c['spice']+c['fining']+c['flavor']
    c['fermentable'] = c['grain']+c['extract']+c['hoppedextract']
    data = []
    try:
        for model in c[ingredient]:
            data += list(globals()[model].select().orderBy('name'))
    except KeyError:
        all_ingredients = {'error': 'No ingredients exist with the name %s' % ingredient}
    else:
        all_ingredients = [sqlobject_to_dict(ing) for ing in data]
    return json.dumps(all_ingredients)