class Unit:

    def __str__(self):
        return 'Unit'


class Bool():

    def __str__(self):
        return 'Bool'


class Nat():

    def __str__(self):
        return 'Nat'
    

class Any():

    def __str__(self):
        return 'Any'
    

class Panic(Any):

    def __str__(self):
        return 'Panic'
    

class Tuple():

    def __init__(self, terms: list):
        self.terms = terms


    def __getitem__(self, index: int):
        if index - 1 >= len(self.terms):
            raise IndexError(f'Index outside the tuple: {index}')

        return self.terms[index-1]
    

    def __str__(self):
        return '{' + ','.join([str(term) for term in self.terms]) + '}'


class Record():

    def __init__(self, dict_: dict):
        self.dict_ = dict_


    def __getitem__(self, key: str):
        if key not in self.dict_:
            raise KeyError(f'{key} not in record')

        return self.dict_[key]
    

    def __str__(self):
        return '{' + ','.join([f'{key}:{str(value)}' for key, value in self.dict_.items()]) + '}'


class Sum():

    def __init__(self, left, right):
        self.left = left
        self.right = right


    def __str__(self):
        return f'({str(self.left)}+{str(self.right)})'


class Fun():

    def __init__(self, param_type, return_type):
        self.param_type = param_type
        self.return_type = return_type


    def __str__(self):
        return f'(fn({str(self.param_type)})->{str(self.return_type)})'


class Ref():

    def __init__(self, type):
        self.type = type

    
    def __str__(self):
        return f'&({str(self.type)})'
    

def issametype(expected, actual):
    ''' 
    compares two types.
    if expected == actual or actual <: expected returns true
    '''
    if isinstance(expected, Any) or isinstance(actual, Any):
        return True

    if type(expected) != type(actual):
        return False

    if isinstance(expected, Bool) or isinstance(expected, Nat) or isinstance(expected, Unit):
        return True
    
    if isinstance(expected, Ref):
        return issametype(expected.type, actual.type)
    
    if isinstance(expected, Record):
        return issubtype(actual, expected)
    
    if isinstance(expected, Fun):
        return issubtype(actual, expected)
    
    if isinstance(expected, Tuple):
        for term_expected, term_actual in zip(expected.terms, actual.terms):
            if not issametype(term_expected, term_actual):
                return False
            
        return True
    
    if isinstance(expected, Sum):
        return (issametype(expected.left, actual.left) and 
                issametype(expected.right, actual.right))
    

def issubtype(actual, expected):
    '''
    true if actual <: expected
    '''
    if isinstance(expected, Record):
        for key, value in expected.dict_.items():
            if key not in actual.dict_:
                return False
            
            if not issametype(value, actual.dict_[key]):
                return False
            
        return True

    if isinstance(expected, Fun):
        return (issubtype(expected.param_type, actual.param_type) and 
                issubtype(actual.return_type, expected.return_type))

    return issametype(expected, actual)
