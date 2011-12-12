from decimal import Decimal, InvalidOperation

from flask import session
from flaskext.wtf import Form, TextField, SelectField, ValidationError, BooleanField
from flaskext.wtf.html5 import IntegerField, DecimalField
from wtforms.validators import Required, Optional, Length
from wtforms.widgets import HiddenInput

from beerlog.brewery.models import *
from beerlog.brewery.measures import Measure

NAME_REQ = "You must provide a name for your recipe"
NAME_LEN = "The name of your recipe cannot be any longer than 64 characters"
STYLE_REQ = "You must select a style for your beer"
RECIPE_TYPE_REQ = "You must select a type for your recipe"
BOIL_VOL_REQ = "You must provide a volume for the recipe's boil"
BOIL_VOL_TYPE_REQ = "You must tell me what units your boil will measure in"
EQUIPMENT_REQ = "You must choose an equipment set for me to accurately handle the boil"
OG_REQ = ''
FG_REQ = ''
SRM_REQ = ''
IBU_REQ = ''
FERM_TYPE_REQ = ''

class DecimalValidation(object):
    def __init__(self, size, places, message=None):
        if not message:
            self.message = "This value must be less than %s^-%s" % (size, places)
        else:
            self.message = message

    def __call__(self, form, field):
        if not isinstance(field.data, Decimal):
            try:
                dec_data = Decimal(field.data)
                field.data = dec_data
            except InvalidOperation:
                raise ValidationError(self.message)
        if field.data.as_tuple.exponent > self.places:
            raise ValidationError(self.message)
        elif field.data.as_tuple.digits[0] > size:
            raise ValidationError(self.message)

class SRMValidation(DecimalValidation):
    def __init__(self, message=None):
        super(SRMValidation, self).__init__(3, 1, message)

class SGValidation(DecimalValidation):
    def __init__(self, message=None):
        super(SGValidation, self).__init__(1, 3, message)

class IBUValidation(DecimalValidation):
    def __init__(self, message=None):
        super(IBUValidation, self).__init__(3, 1, message)

class PercentValidation(DecimalValidation):
    def __init__(self, message=None):
        super(PercentValidation, self).__init__(3, 2, message)

class TemperatureValidation(DecimalValidation):
    def __init__(self, message=None):
        super(TemperatureValidation, self).__init__(3, 1, message)
    
def style_choices():
    styles = BJCPStyle.select().orderBy('category_id').orderBy('subcategory')
    return [(s.id, s.name) for s in styles]

def recipe_type_choices():
    return [(Recipe.recipe_types.index(x), x) for x in Recipe.recipe_types]
    
def boil_volume_choices():
    return [(Measure.GAL, Measure.measures[Measure.GAL]),
            (Measure.LITER, Measure.measures[Measure.LITER])]

def equipment_set_choices():
    equipment = EquipmentSet.select(EquipmentSet.q.brewer==session.get('user_id'))
    return [(e.id, e.name) for e in equipment]

def fermentation_type_choices():
    return [(Recipe.fermentation_types.index(x), x) for x in Recipe.fermentation_types]
    
def temp_unit_choices():
    return [(Measure.F, Measure.temperatures[Measure.F]),
             (Measure.C, Measure.temperatures[Measure.C])]

def time_unit_choices():
    return [(Measure.DAYS, Measure.timing_parts[Measure.DAYS]),
            (Measure.WEEKS, Measure.timing_parts[Measure.WEEKS])]

def mash_choices():
    return [(m.id, m.name) for m in MashProfile.select()]
    
def carbonation_choices():
    return [(Recipe.carbonation_types.index(x), x) for x in Recipe.carbonation_types]
    
def small_weight_choices():
    return [(Measure.GM, Measure.measures[Measure.GM]),
            (Measure.OZ, Measure.measures[Measure.OZ])]
    
class RecipeForm(Form):
    name = TextField("Name", 
                     [Required(message=NAME_REQ),
                      Length(min=1, max=64, message=NAME_LEN)])
    style = SelectField("Style", 
                        coerce=int,
                        choices=style_choices(), 
                        validators=[Required(STYLE_REQ)])
    brewer = IntegerField(widget=HiddenInput())
    recipe_type = SelectField("Recipe Type",
                              coerce=int,
                              choices=recipe_type_choices(),
                              validators=[Required(RECIPE_TYPE_REQ)])
    boil_volume = DecimalField('Boil Volume', 
                               places=2,
                               validators=[Required(BOIL_VOL_REQ)])
    boil_volume_units = SelectField(choices=boil_volume_choices(),
                                    coerce=int,
                                    validators=[Required(BOIL_VOL_TYPE_REQ)])
    batch_volume = DecimalField('Batch Volume', 
                               places=2,
                               validators=[Required(BOIL_VOL_REQ)])
    batch_volume_units = SelectField(choices=boil_volume_choices(),
                                    coerce=int,
                                    validators=[Required(BOIL_VOL_TYPE_REQ)])
    equipment = SelectField("Equipment",
                            coerce=int,
                            choices=equipment_set_choices(),
                            validators=[Required(EQUIPMENT_REQ)])
    base_boil_equipment = BooleanField("Base boil on equipment", [Optional()])
    efficiency = IntegerField("Efficiency", [Optional()])
    og = DecimalField("O.G.",
                      places=3,
                      validators=[Required(OG_REQ), SGValidation()])
    fg = DecimalField("F.G.",
                      places=3,
                      validators=[Required(FG_REQ), SGValidation()])
    color = DecimalField("Color",
                         places=1,
                         validators=[Required(SRM_REQ), SRMValidation()])

    ibu = DecimalField("IBUs",
                       places=1,
                       validators=[Required(IBU_REQ), IBUValidation()])
    # ingredients are stored in hidden textfields which contain json-formatted
    # strings containing the list of ingredients for that type, as well as
    # all the other relevant ingredient data
    # example: [{"id": ingredient.id
    #            "amount": ingredient amount & unit}
    #            "use": where ingredient is used
    #            "time": amount of time from end of boil thing should be used}]
    hops = TextField(widget=HiddenInput())
    grains = TextField(widget=HiddenInput())
    extracts = TextField(widget=HiddenInput())
    hopped_extracts = TextField(widget=HiddenInput())
    mineral = TextField(widget=HiddenInput())
    fining = TextField(widget=HiddenInput())
    flavor = TextField(widget=HiddenInput())
    spice = TextField(widget=HiddenInput())
    herb = TextField(widget=HiddenInput())
    fermentation_type = SelectField("Fermentation",
                                    coerce=int,
                                    choices=fermentation_type_choices(),
                                    validators=[Required(FERM_TYPE_REQ)])
    stage_1_temp = DecimalField("First stage", [TemperatureValidation(), 
                                                Required()])
    stage_1_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Required()])
    stage_1_time = IntegerField("Time", [Required()])
    stage_1_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators=[Required()])
    stage_2_temp = DecimalField("Second Stage", [TemperatureValidation(), 
                                                Optional()])
    stage_2_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Optional()])
    stage_2_time = IntegerField("Time", [Optional()])
    stage_2_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators=[Optional()])
    stage_3_temp = DecimalField("Third Stage", [TemperatureValidation(), 
                                                Optional()])
    stage_3_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Optional()])
    stage_3_time = IntegerField("Time", [Optional()])
    stage_3_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators=[Optional()])
    mash = SelectField("Mash Profile",
                        coerce=int,
                        choices=mash_choices(),
                        validators=[Optional()])
    carbonation_type = SelectField("Carbonation Type",
                                    coerce=int,
                                    choices=carbonation_choices(),
                                    validators=[Optional()])
    carbonation_volume = DecimalField('Volume wanted', 
                                      places=1,
                                      validators=[Optional()])
    carbonation_sugar_amount = DecimalField("Amount",
                                            places=2,
                                            validators=[Optional()])
    carbonation_sugar_units = SelectField(coerce=int,
                                          choices=small_weight_choices(),
                                          validators=[Optional()])