#!/usr/bin/env python

# BeerMaker - beer recipe creation and inventory management software
# Copyright (C) 2010 Todd Kennedy <todd.kennedy@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xml.dom import minidom
import os

from sqlobject import *
from sqlobject.dberrors import DuplicateEntryError

from beerlog.brewery.measures import Measure
from beerlog.brewery.models import Hop, Grain, Extract, HoppedExtract, Yeast,\
                                   Fining, Mineral, Flavor, Spice, Herb,\
                                   Misc, BJCPCategory, BJCPStyle
from beerlog.brewery.beerutils import sg_from_yield, c2f
from beerlog.settings import data_dir

def process_bjcp_styles():
    # import the XML
    styledoc = minidom.parse(os.path.join(data_dir, 'styleguide2008.xml'))
    # generate categories
    for beer_class in styledoc.getElementsByTagName('class'):
        this_class = unicode(beer_class.getAttribute('type'))
        for category in beer_class.getElementsByTagName('category'):            
            nameN = category.getElementsByTagName('name')[0]
            name = unicode(nameN.firstChild.data)
            category_id = int(category.getAttribute('id'))
            notes = ""
            if category.getElementsByTagName('notes'):
                for note in category.getElementsByTagName('notes'):
                    for child in note.childNodes:
                        notes = notes + "\n\n" + child.toxml()
            try:
                this_category = BJCPCategory(name=name,
                                             category_id=category_id,
                                             notes=notes)
            except DuplicateEntryError:
                this_category = BJCPCategory.selectBy(category_id=category_id)
            # generate styles for this category
            for sc in category.getElementsByTagName('subcategory'):
                # we're only interested in the last letter -- 
                # the number is duplicative data
                subcategory_id = unicode(sc.getAttribute('id')[-1:]).upper()
                # initialize the variables needed
                name = aroma = flavor = appearance = mouthfeel = None
                impression = comments = examples = None
                og_low = og_high = abv_high = fg_low = fg_high = srm_low = 0
                srm_high = abv_low = ibu_low = ibu_high = 0

                g = sc.getElementsByTagName
                # loop over the text nodes and set the value of the 
                # node equal to the xml node name
                try:
                    name = unicode(g('name')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    aroma = unicode(g('aroma')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    appearance = unicode(g('appearance')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    flavor = unicode(g('flavor')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    mouthfeel = unicode(g('mouthfeel')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    impression = unicode(g('impression')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    comments = unicode(g('comments')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass
                try:
                    examples = unicode(g('examples')[0].firstChild.data)
                except (IndexError, AttributeError):
                    pass

                s = g('stats')[0].getElementsByTagName
        
                if not s('exceptions'):                
                    try:
                        ibu_lowN = s('ibu')[0].getElementsByTagName('low')[0]
                        ibu_low = int(ibu_lowN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        ibu_highN = s('ibu')[0].getElementsByTagName('high')[0]
                        ibu_high = int(ibu_highN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        og_lowN = s('og')[0].getElementsByTagName('low')[0]
                        og_low = float(og_lowN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        og_highN = s('og')[0].getElementsByTagName('high')[0]
                        og_high = float(og_highN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        fg_lowN = s('fg')[0].getElementsByTagName('low')[0]
                        fg_low = float(fg_lowN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        fg_highN = s('fg')[0].getElementsByTagName('high')[0]
                        fg_high = float(fg_highN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        srm_lowN = s('srm')[0].getElementsByTagName('low')[0]
                        srm_low = float(srm_lowN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        srm_highN = s('srm')[0].getElementsByTagName('high')[0]
                        srm_high = float(srm_highN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        abv_lowN = s('abv')[0].getElementsByTagName('low')[0]
                        abv_low = float(abv_lowN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass
                    try:
                        abv_highN = s('abv')[0].getElementsByTagName('high')[0]
                        abv_high = float(abv_highN.firstChild.data)
                    except (IndexError, AttributeError):
                        pass        
                BJCPStyle(name = name, 
                    beer_type = this_class, 
                    category = this_category,
                    subcategory = subcategory_id,                      
                    aroma = aroma,
                    appearance = appearance,
                    flavor = flavor,
                    mouthfeel = mouthfeel,
                    impression = impression,
                    comments = comments,
                    examples = examples,
                    og_low = og_low,
                    og_high = og_high,
                    fg_low = fg_low,
                    fg_high = fg_high,
                    srm_low = srm_low,
                    srm_high = srm_high,
                    ibu_low = ibu_low,
                    ibu_high = ibu_high,
                    abv_low = abv_low,
                    abv_high = abv_high)
                    
def process_bt_database():
    d = minidom.parse(os.path.join(data_dir, '/beer_data.xml'))
    #print "adding hops"
    process_hops(d)
    #print "adding fermentables"
    process_fermentables(d)
    #print "adding yeasts"
    process_yeasts(d)
    #print "adding miscellaneous"
    process_misc(d)
    
def process_hops(d):
    # process all the hops
    for hop in d.getElementsByTagName('HOP'):
        g = hop.getElementsByTagName
        name = origin = substitutes = description = None
        alpha = beta = hop_type = hop_form = stability = 0
        
        try:
            name = unicode(g('NAME')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            alpha = float(g('ALPHA')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            beta = float(g('BETA')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            origin = unicode(g('ORIGIN')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            substitutes = unicode(g('SUBSTITUTES')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            description = unicode(g('NOTES')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            hop_type = Hop.hop_types.index(g('TYPE')[0].firstChild.data)
        except AttributeError:
            pass
        try:    
            hop_form = 0
        except AttributeError:
            pass
        try:    
            stability = float(g('HSI')[0].firstChild.data)
        except AttributeError:
            pass
        
        substitute_hops = []
        try:
            for sub_hop in substitutes.split(','):
                try:
                    sh = list(Hop.select(Hop.q.name==sub_hop.strip()))[0]
                except (SQLObjectNotFound, IndexError):
                    sh = Hop(name=sub_hop.strip())
                substitute_hops.append(sh)
        except AttributeError:
            pass

        #print "adding hop: %s" % name
        thisHop = Hop(name=name,
            alpha=alpha,
            beta=beta,
            origin=origin,
            description=description,
            hop_type=hop_type,
            hop_form=hop_form,
            stability=stability
            )
        if substitute_hops:
            [thisHop.addSubstitute(x) for x in substitute_hops]

def process_fermentables(d):
    # process all the fermentables
    for f in d.getElementsByTagName('FERMENTABLE'):
        g = f.getElementsByTagName
        key = g('TYPE')[0].firstChild.data.lower()
        # grains...
        if key == 'grain' or key == 'adjunct':
            # set the grain defaults
            name = origin = maltster = notes = None
            color = potential = dry_yield_fine_grain = 0
            coarse_fine_difference = moisture = 0
            diastatic_power = max_in_batch = protein = 0
            must_mash = add_after_boil = True
            
            try:
                name = unicode(g('NAME')[0].firstChild.data)
            except AttributeError:
                pass
            try:
                origin = unicode(g('ORIGIN')[0].firstChild.data)
            except AttributeError:
                pass
            try:
                maltster = unicode(g('SUPPLIER')[0].firstChild.data)
            except AttributeError:
                pass
            try:
                color = float(g('COLOR')[0].firstChild.data)
            except AttributeError:
                pass
            try:    
                potential = sg_from_yield(float(g('YIELD')[0].firstChild.data))
            except AttributeError:
                pass
            try:    
                dry_yield_fine_grain = float(g('YIELD')[0].firstChild.data)
            except AttributeError:
                pass
            try:  
                cfd = g('COARSE_FINE_DIFF')[0].firstChild.data
                coarse_fine_difference = float(cfd)                
            except AttributeError:
                pass
            try:    
                moisture = float(g('MOISTURE')[0].firstChild.data)
            except AttributeError:
                pass
            try:    
                diastatic_power = float(g('DIASTATIC_POWER')[0].firstChild.data)
            except AttributeError:
                pass
            try:    
                max_in_batch = float(g('MAX_IN_BATCH')[0].firstChild.data)
            except AttributeError:
                pass
            try:    
                if g('IS_MASHED')[0].firstChild.data == 'FALSE':
                    must_mash = False
                else:
                    must_mash = True
            except AttributeError:
                pass
            try:    
                if g('ADD_AFTER_BOIL')[0].firstChild.data == 'FALSE':
                    add_after_boil = False
                else:
                    add_after_boil = True
            except AttributeError:
                pass
            try:    
                notes = unicode(g('NOTES')[0].firstChild.data)
            except AttributeError:
                pass                
            #print 'adding grain: %s' % name
            thisGrain = Grain(name=name,
                origin=origin,
                maltster=maltster,
                color=color,
                potential=potential,
                dry_yield_fine_grain=dry_yield_fine_grain,
                coarse_fine_difference=coarse_fine_difference,
                moisture=moisture,
                diastatic_power=diastatic_power,
                max_in_batch=max_in_batch,
                must_mash=must_mash,
                add_after_boil=add_after_boil,
                notes=notes)
        elif key == 'extract' or key == 'sugar' or key == 'dry extract':
            name = origin = supplier = notes = None
            color = potential = max_in_batch = 0
            add_after_boil = False
            try:
                name = unicode(g('NAME')[0].firstChild.data)
            except AttributeError:
                 pass
            try:                 
                origin = unicode(g('ORIGIN')[0].firstChild.data)
            except AttributeError:
                 pass
            try:
                 supplier = unicode(g('SUPPLIER')[0].firstChild.data)
            except AttributeError:
                 pass
            try:
                notes = unicode(g('NOTES')[0].firstChild.data)
            except AttributeError:
                 pass
            try:
                color = float(g('COLOR')[0].firstChild.data)
            except AttributeError:
                 pass
            try:
                potential = sg_from_yield(float(g('YIELD')[0].firstChild.data))
            except AttributeError:
                 pass
            try:    
                max_in_batch = float(g('MAX_IN_BATCH')[0].firstChild.data)
            except AttributeError:
                 pass
            try:
                if g('ADD_AFTER_BOIL')[0].firstChild.data == 'FALSE':
                    add_after_boil = False
                else:
                    add_after_boil = True
            except AttributeError:
                 pass
            #print "adding extract: %s" % name
            thisExtract = Extract(name=name,
                origin=origin,
                supplier=supplier,
                notes=notes,
                color=color,
                potential=potential,
                max_in_batch=max_in_batch,
                add_after_boil=add_after_boil)
                
def process_yeasts(d):            
    for y in d.getElementsByTagName('YEAST'):
        g = y.getElementsByTagName
        #set some reasonable defaults
        name = lab = yeast_id = best_for = notes = None
        yeast_type = yeast_form = flocc = starter_size =\
            starter_units = avg_attenuation = min_temp =\
            max_temp = temp_units = max_reuse = 0
        use_starter = secondary = False 
        try:
            name = unicode(g('NAME')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            yeast_type = Yeast.yeast_types.index(g('TYPE')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            yeast_form = Yeast.yeast_forms.index(g('FORM')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            yeast_id = unicode(g('PRODUCT_ID')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            flocc_idx = g('FLOCCULATION')[0].firstChild.data
            flocc = Yeast.yeast_flocculations.index(flocc_idx)
        except AttributeError:
            pass
        try:
            avg_attenuation = float(g('ATTENUATION')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            min_temp = c2f(float(g('MIN_TEMPERATURE')[0].firstChild.data))
        except AttributeError:
            pass
        try:
            max_temp = c2f(float(g('MAX_TEMPERATURE')[0].firstChild.data))
        except AttributeError:
            pass
        try:
            max_reuse = int(g('MAX_REUSE')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            best_for = unicode(g('BEST_FOR')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            notes = unicode(g('NOTES')[0].firstChild.data)
        except AttributeError:
            pass            
        try:
            if g('ADD_TO_SECONDARY')[0].firstChild.data == 'FALSE':
                add_to_secondary = False
            else:
                add_to_secondary = True
        except AttributeError:
            pass
        try:
            amount = float(g('AMOUNT')[0].firstChild.data)*1000
        except AttributeError:
            pass
        try:
            if g('AMOUNT_IS_WEIGHT')[0].firstChild.data == 'FALSE':
                amount_units = Measure.ML
            else:
                amount_units = Measure.GM
        except AttributeError:
            pass
        temp_units = Measure.FAHRENHEIT            
        if yeast_type == Yeast.yeast_forms.index('Liquid'):
            use_starter = True
        else:
            use_starter = False
        #print "adding yeast: %s" % name
        thisYeast = Yeast(name=name,
            yeast_type=yeast_type,
            yeast_form=yeast_form,
            yeast_id=yeast_id,
            flocc=flocc,
            avg_attenuation=avg_attenuation,
            min_temp=min_temp,
            max_temp=max_temp,
            max_reuse=max_reuse,
            best_for=best_for,
            notes=notes,
            secondary=add_to_secondary,
            temp_units=temp_units,
            use_starter=use_starter,
            amount=amount,
            amount_units=amount_units)

def process_misc(d):
    for m in d.getElementsByTagName('MISC'):
        g = m.getElementsByTagName        
        herbs = ['Heather Tips', ]
        spices = ['Whole Coriander',
                  'Vanilla Beans',
                  'Paradise Seed',
                  'Licorice Root',
                  'Bitter Orange Peel',
                  'Sweet Orange Peel']
        misc_type = g('TYPE')[0].firstChild.data
        if misc_type == "Fining":
            misc_obj = Fining
        elif misc_type == 'Other':
            misc_obj = Misc
        elif misc_type == 'Flavor':
            misc_obj = Flavor
        elif misc_type == 'Water Agent':
            misc_obj = Mineral
        else:
            #print "No matched type, boss %s" % misc_type
            pass
        name = use_for = notes = None
        rec_amount = rec_units = batch_size = batch_size_units = \
            use_in = use_time = use_time_units = 0
        try:
            name = unicode(g('NAME')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            use_for = unicode(g('USE_FOR')[0].firstChild.data)
        except AttributeError:
            pass
        try:
            use_in = Misc.misc_use_ins.index(g('USE')[0].firstChild.data)
        except AttributeError:
            pass        
        if name in herbs and misc_obj == Flavor:
            misc_obj = Herb
        if name in spices and misc_obj == Flavor:
            misc_obj = Spice     
        if name == u'Paradise Seed':
            name = u'Grains of Paradise'
        #print "adding misc: %s" % name
        thisMisc = misc_obj(name=name,
            use_for=use_for,
            rec_amount=rec_amount,
            rec_units=rec_units,
            batch_size=batch_size,
            batch_size_units=batch_size_units,
            use_in=use_in,
            use_time=use_time,
            use_time_units=use_time_units)