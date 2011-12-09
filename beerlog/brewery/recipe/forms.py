from decimal import Decimal

from flask import session
from flaskext.wtf import Form, TextField, SelectField, 
from flaskext.wtf.html5 import IntegerField, DecimalField
from wtforms.validators import Required, Optional, Length, ValidatonError
from wtforms.widgets import HiddenInput

from beerlog.brewery.models import BJCPStyle
from beerlog.brewery.measures import Measure

NAME_REQ = "You must provide a name for your recipe"
NAME_LEN = "The name of your recipe cannot be any longer than 64 characters"
STYLE_REQ = "You must select a style for your beer"
RECIPE_TYPE_REQ = "You must select a type for your recipe"
BOIL_VOL_REQ = "You must provide a volume for the recipe's boil"
BOIL_VOL_TYPE_REQ = "You must tell me what units your boil will measure in"
EQUIPMENT_REQ = "You must choose an equipment set for me to accurately handle the boil"

class SGValidation():
    def __init__(self, message=None):
        if not message:
            self.message = "This must be a standard gravity value"
        else:
            self.message = message            
            
    def __call__(self, form, field):
        if not isinstance(field.data, Decimal):
            raise ValidationError(self.message)
        else:
            if field.data.as_tuple.exponent != 3:
                raise ValidationError(self.message)
            elif field.data.as_tuple.digits[0] > 1:
                raise ValidationError(self.message)

def get_style_choices():
    styles = BJCPStyle.select().orderBy('category_id', 'subcategory')
    return [(s.id, s.name) for s in styles]

def get_recipe_type_choices():
    return [(Recipe.recipe_types.index(x), x) for x in Recipe.recipe_types]
    
def boil_volume_choices():
    return [(Measure.GAL, Measure.measures.index(Measure.GAL),
            (Measure.LITER, Measure.measures.index(Measure.LITER)]

def equipment_set_choices():
    equipment = EquipmentSet.select(EquipmentSet.brewer==session.user_id)
    return [(e.id, e.name) for e in equipment]
            
class RecipeForm(Form):
    name = TextField("Name", 
                     [Required(message=NAME_REQ,
                      Length(min=1, max=64, message=NAME_LEN_ERROR)])
    style = SelectField("Style", 
                        coerce=int,
                        choices=get_style_choices(), 
                        validators=[Required(STYLE_REQ)])
    brewer = IntegerField(widget=HiddenInput())
    recipe_type = SelectField("Recipe Type",
                              coerce=int,
                              choices=get_recipe_type_choices(),
                              validators=[Required(RECIPE_TYPE_REQ])
    boil_volume = DecimalField('Boil Volume', 
                               places=2,
                               validators=[Required(BOIL_VOL_REQ])
    boil_volume_units = SelectField(choices=boil_volume_choices(),
                                    coerce=int,
                                    validators=[Required(BOIL_VOL_TYPE_REQ)])
    equipment = SelectField("Equipment",
                            coerce=int,
                            choices=equipment_set_choices(),
                            validators=[Required(EQUIPMENT_REQ)])
    base_boil_equipment = BooleanField("Base boil on equipment", [Optional()])
    efficiency = IntegerField("Efficiency", [Optional()])
    og = DecimalField("OG",
                      places=3,
                      validators[Required(OG_REQ), SGValidation()])
    fg = DecimalField("FG",
                      places=3,
                      validators[Required(FG_REQ), SGValidation()])
    color = DecimalField("SRM",
                         places=1,
                         validators[Required(SRM_REQ), SRMValidation()])

    
    color = SRMCol(default=0)
    ibu = IBUCol(default=0)
    ingredient = MultipleJoin('RecipeIngredient')
    fermentation_type = IntCol(default=SINGLE)
    fermentation_stage_1_temp = DecimalCol(size=5, precision=2, default=0)
    fermentation_stage_1_temp_units = IntCol(default=Measure.F)
    fermentation_stage_2_temp = DecimalCol(size=5, precision=2, default=0)
    fermentation_stage_2_temp_units = IntCol(default=Measure.F)
    fermentation_stage_3_temp = DecimalCol(size=5, precision=2, default=0)
    fermentation_stage_3_temp_units = IntCol(default=Measure.F)
    fermentation_stage_1_length = IntCol(default=0)
    fermentation_stage_2_length = IntCol(default=0)
    fermentation_stage_3_length = IntCol(default=0)
    fermentation_stage_1_length_units = IntCol(default=0)
    fermentation_stage_2_length_units = IntCol(default=0)
    fermentation_stage_3_length_units = IntCol(default=0)
    mash = ForeignKey('MashProfile', default=None)
    carbonation_type = IntCol(default=FORCED_CO2)
    carbonation_volume = DecimalCol(size=3, precision=1, default=0)
    carbonation_amount = DecimalCol(size=4, precision=2, default=0)
    carbonation_amount_units = IntCol(default=Measure.OZ)
    brewed_on = DateCol(default=datetime.now())
    is_batch = BoolCol(default=False)
    master_recipe = IntCol(default=0)
    grain_total_weight = DecimalCol(size=5, precision=2, default=0)
    hop_total_weight = DecimalCol(size=5, precision=2, default=0)