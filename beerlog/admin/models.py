import re
import hashlib
from datetime import datetime

from sqlobject import *

from beerlog.image.models import Image
from beerlog.settings import PASSWORD_SALT

class Users(SQLObject):
    first_name = UnicodeCol(length=128)
    last_name = UnicodeCol(length=128)
    email = UnicodeCol(length=255, unique=True)
    alias = UnicodeCol(length=255)
    password = UnicodeCol(length=255, default="sdlfjskdfjskdfjsadf")
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    last_login = DateTimeCol(default=datetime.now())
    avatar = ForeignKey("Image", notNone=False, default=None)
    active = BoolCol(default=True)
    role = RelatedJoin('Role')
    admin = BoolCol(default=False)
    
    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)
        
    def _get_memberships(self):
        return self.role.memberships()

def generate_password(cleartext):
    cyphertext = hashlib.sha256("%s%s" % (PASSWORD_SALT, cleartext))
    return cyphertext.hexdigest()        
    

class Role(SQLObject):
    name = UnicodeCol(length=128)
    user = RelatedJoin('Users')
    memberships= RelatedJoin('Role',
                             joinColumn='master_role',
                             otherColumn='sub_role',
                             addRemoveName='Membership',
                             intermediateTable='role_to_role_relations',
                             createRelatedTable=True)
                             
    def _get_memeberships(self):
        return self.memberships + [self,]

# class Permission(SQLObject):
#     EDIT_DELETE_READ = 7
#     EDIT_READ = 6
#     READ_DELETE = 5
#     READ = 4
#     EDIT_DELETE = 3
#     EDIT = 2
#     DELETE = 1
#     NONE = 0
#     permissions = ['none', 'delete', 'edit', 'edit & delete', 'read', 
#                    'read & delete', 'edit & read', 'edit, delete & read']
#     
#     role = RelatedJoin('Role')
#     user = RelatedJoin('Users')
#     object_type = UnicodeCol(length=128)
#     object_id = IntCol()
#     permission = IntCol(default=EDIT_DELETE_READ)
#     
#     def _set_object_id(self, value):
#         self.object_type = value.__class__.__name__
#         self._SO_set_object_id = value.id