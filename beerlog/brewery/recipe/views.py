from flask import render_template

from beerlog.brewery.models import *
from beerlog.brewery.recipe.forms import RecipeForm

@app.route('/brewery/')
@app.route('/brewery/recipe/')
@app.route('/brewery/recipe/<recipe_id>/batch/')
def list_recipes(recipe_id = -1):
    pass

@app.route('/brewery/recipe/<recipe_id>/')
@app.route('/brewery/recipe/batch/<recipe_id>/')
def edit_recipe(recipe_id=-1):
    recipe_form = RecipeForm()
    if recipe_form.validate_on_submit():
        pass
    else:
        pass
        
    
    
