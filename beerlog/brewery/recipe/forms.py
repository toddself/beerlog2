from decimal import Decimal, InvalidOperation

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

class DecimalValidation():
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
        super(DecimalValidation, self).__init__(3, 1, message)

class SGValidation(DecimalValidation):
    def __init__(self, message=None):
        super(DecimalValidation, self).__init__(1, 3, message)

class IBUValidation(DecimalValidation):
    def __init__(self, message=None):
        super(DecimalValidation, self).__init__(3, 1, message)

class PercentValidation(DecimalValidation):
    def __init__(self, message=None):
        super(DecimalValidation, self).__init__(3, 2, message)

class TemperatureValidation(DecimalValidation):
    def __init__(self, message=None):
        super(DecimalValidation, self).__init__(3, 1, message)
    
def style_choices():
    styles = BJCPStyle.select().orderBy('category_id', 'subcategory')
    return [(s.id, s.name) for s in styles]

def recipe_type_choices():
    return [(Recipe.recipe_types.index(x), x) for x in Recipe.recipe_types]
    
def boil_volume_choices():
    return [(Measure.GAL, Measure.measures.index(Measure.GAL),
            (Measure.LITER, Measure.measures.index(Measure.LITER)]

def equipment_set_choices():
    equipment = EquipmentSet.select(EquipmentSet.brewer==session.user_id)
    return [(e.id, e.name) for e in equipment]

def fermentation_type_choices():
    return [(Recipe.fermentation_types.index(x), x) for x in Recipe.fermentation_types]
    
def temp_unit_choices():
    return [(Measure.F, Measure.temperatures.index(Measure.F)),
             Measure.C, Measure.temperatures.index(Measure.C)]

def time_unit_choices():
    return [(Measure.DAYS, Measure.timing_parts.index(Measure.DAYS)),
            (Measure.WEEKS, Measure.timing_parts.index(Measure.WEEKS))]  

def mash_choices():          

class RecipeForm(Form):
    name = TextField("Name", 
                     [Required(message=NAME_REQ,
                      Length(min=1, max=64, message=NAME_LEN_ERROR)])
    style = SelectField("Style", 
                        coerce=int,
                        choices=style_choices(), 
                        validators=[Required(STYLE_REQ)])
    brewer = IntegerField(widget=HiddenInput())
    recipe_type = SelectField("Recipe Type",
                              coerce=int,
                              choices=recipe_type_choices(),
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

    ibu = DecimalField("IBU",
                       places=1,
                       validators[Required(IBU_REQ), IBUValidation()])
    # ingredients are stored in hidden textfields which contain json-formatted
    # strings containing the list of ingredients for that type, as well as
    # all the other relevant ingredient data
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
    stage_1_temp = DecimalField("Temperature", [TemperatureValidation(), 
                                                Required()])
    stage_1_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Required()])
    stage_1_time = IntegerColumn("Time", [Required()])
    stage_1_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators[Required()])
    stage_2_temp = DecimalField("Temperature", [TemperatureValidation(), 
                                                Optional()])
    stage_2_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Optional()])
    stage_2_time = IntegerColumn("Time", [Optional()])
    stage_2_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators[Optional()])
    stage_3_temp = DecimalField("Temperature", [TemperatureValidation(), 
                                                Optional()])
    stage_3_temp_units = SelectField(coerce=int,
                                     choices=temp_unit_choices(),
                                     validators=[Optional()])
    stage_3_time = IntegerColumn("Time", [Optional()])
    stage_3_time_units = SelectField(coerce=int,
                                     choices=time_unit_choices(),
                                     validators[Optional()])
    mash = SelectColumn(coerce=int,
                        choices=mash_choices(),
                        validators=[Optional()])





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