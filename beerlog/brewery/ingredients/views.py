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
                  'fining': ['Fining',]}
    c['misc'] = c['mineral']+c['herb']+c['spice']+c['fining']+c['flavor']
    c['fermentables'] = c['grain']+c['extract']+c['hoppedextract']
    data = []
    for model in c[ingredient]:
        data += list(globals()[model].select().orderBy('name'))
    all_ingredients = [sqlobject_to_dict(ing) for ing in data]
    return json.dumps(all_ingredients)