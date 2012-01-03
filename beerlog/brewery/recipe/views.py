import json

from flask import render_template, flash, url_for

from beerlog.brewery.models import *
from beerlog.brewery.recipe.forms import RecipeForm
from beerlog.helpers import sqlobject_to_dict

def list_recipes(recipe_id = -1):
    pass

def edit_recipe(recipe_id=-1):
    recipe_form = RecipeForm()
    if recipe_form.validate_on_submit():
        pass
    else:
        recipe = {'id': None}
        return render_template('edit_recipe.html', data={'form': recipe_form,
                                                         'recipe': recipe})

def pymodel_as_json(model):
    model_name = model[0].capitalize()+model[1:]
    model_instance = globals()[model_name]()
    pydict = sqlobject_to_dict(model_instance).keys()
    pydict.append('id')
    return json.dumps(pydict)