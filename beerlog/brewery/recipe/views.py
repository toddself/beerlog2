from flask import render_template, flash, url_for

from beerlog.brewery.models import *
from beerlog.brewery.recipe.forms import RecipeForm

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