from sqlobject import DecimalCol
from sqlobject.col import pushKey

class SGCol(DecimalCol):
    """ Stores Specific Gravity in a decimal column
    Size is fixed at 4, and the precision is set to 3
    
    ex: 1.045    
    
    """
    
    def __init__(self, **kw):
        pushKey(kw, 'size', 4)
        pushKey(kw, 'precision', 3)
        super(DecimalCol, self).__init__(**kw)

class PercentCol(DecimalCol):
    """Stores percentages in a decimal column
    Size is fixed at 5, and the precision is set to 2.  
    
    *nb* size is fixed at 5 to allow for 100.00%
    
    """
    
    def __init__(self, **kw):
        pushKey(kw, 'size', 5)
        pushKey(kw, 'precision', 2)
        super(DecimalCol, self).__init__(**kw)

class SRMCol(DecimalCol):
    """ Stores the Standard Reference Method color value in a decimal column
    Size is fixed at 5, precision is set to 1
    
    ex: 2.0, 300.5
    
    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 5)
        pushKey(kw, 'precision', 1)
        super(DecimalCol, self).__init__(**kw)

class IBUCol(DecimalCol):
    """ Stores the International Bitterness Units value in a decimal column
    Size is fixed at 4, precision is set to 1
    
    ex: 2.0, 300.5
    
    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 4)
        pushKey(kw, 'precision', 1)
        super(DecimalCol, self).__init__(**kw)        

class BatchIsNotMaster(Exception):
    def __init__(self,value):
        self.value = value
    def __unicode__(self,value):
        return repr(self.value)

class AmountSetError(Exception):
    def __init__(self, value):
        self.value = value
    def __unicode__(self, value):
        return repr(self.value)  