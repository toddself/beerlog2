import json
from decimal import Decimal

from werkzeug import import_string, cached_property 
from sqlobject import SQLObject

def format_time(value, format="%H:%M %m/%d/%Y"):
    return value.strftime(format)
    
def sqlobject_to_dict(obj):
    obj_dict = {}
    cls_name = type(obj)
    has_props = False
    for attr in vars(cls_name):
        attr_parent = type(getattr(obj, attr)).__bases__[0]
        if isinstance(getattr(cls_name, attr), property):
            print 'here'
            has_props = True
            if isinstance(getattr(obj, attr), Decimal):
                obj_dict[attr] = float(getattr(obj, attr))
            elif isinstance(getattr(obj, attr), list):
                dict_list = []
                for list_item in getattr(obj, attr):
                    dict_list.append(sqlobject_to_dict(list_item))
                obj_dict[attr] = dict_list
            elif isinstance(getattr(obj, attr), dict):
                dict_dict = {}
                for key, val in getattr(obj, attr):
                    dict_dict[key] = sqlobject_to_dict(val)
                obj_dict[attr] = dict_dict
            elif attr_parent == SQLObject:
                obj_dict[attr] = sqlobject_to_dict(getattr(obj, attr))
            else:
                obj_dict[attr] = getattr(obj, attr)
        elif not has_props and attr_parent != SQLObject:
            if "_get_" in attr:
                attr_name = '_'.join(attr.split('_', 3)[3:])
                if hasattr(obj, attr_name):
                    obj_dict[attr_name] = getattr(obj, attr_name)
    return obj_dict

class LazyView(object):
    
    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.',  1)
        self.import_name = import_name
        
    @cached_property
    def view(self):
        return import_string(self.import_name)
    
    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)