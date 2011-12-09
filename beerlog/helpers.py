import json
from decimal import Decimal

from sqlobject import SQLObject

def format_time(value, format="%H:%M %m/%d/%Y"):
    return value.strftime(format)
    
def sqlobject_to_dict(obj):
    json_dict = {}
    cls_name = type(obj)
    for attr in vars(cls_name):
        if isinstance(getattr(cls_name, attr), property):
            attr_value = getattr(obj, attr)
            attr_class = type(attr_value)
            attr_parent = attr_class.__bases__[0]
            if isinstance(getattr(obj, attr), Decimal):
                json_dict[attr] = float(getattr(obj, attr))
            elif attr_parent == SQLObject:
                json_dict[attr] = sqlobject_to_dict(getattr(obj, attr))
            else:
                json_dict[attr] = getattr(obj, attr)

    return json_dict