class Unit:

    def __init__(self):
        pass


    def __str__(self):
        return 'Unit'


class Bool():

    def __init__(self):
        pass

    def __str__(self):
        return 'Bool'


class Nat():

    def __init__(self):
        pass


    def __str__(self):
        return 'Nat'
    

class Any():

    def __init__(self):
        pass


    def __str__(self):
        return 'Any'
    

class Tuple():

    def __init__(self, terms):
        self.terms = terms


    def __getitem__(self, index):
        if index - 1 >= len(self.terms):
            raise IndexError(f'Index outside the tuple: {index}')

        return self.terms[index-1]
    

    def __str__(self):
        return '{' + ','.join([str(term) for term in self.terms]) + '}'

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


def compare_types(expected, actual):
    '''
    compares two types
    if expected == actual return true
    '''
    if isinstance(expected, Any) or isinstance(actual, Any):
        return True

    if type(expected) != type(actual):
        return False

    if isinstance(expected, Bool) or isinstance(expected, Nat) or isinstance(expected, Unit):
        return True
    
    if isinstance(expected, Fun):
        return (compare_types(expected.param_type, actual.param_type) and 
                compare_types(expected.return_type, actual.return_type))
    
    if isinstance(expected, Tuple):
        for term_expected, term_actual in zip(expected.terms, actual.terms):
            if not compare_types(term_expected, term_actual):
                return False
            
        return True
    
    if isinstance(expected, Sum):
        return (compare_types(expected.left, actual.left) and 
                compare_types(expected.right, actual.right))
