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


class Tuple():

    def __init__(self, terms):
        self.terms = terms


    def __getitem__(self, index):
        if index - 1 >= len(self.terms):
            raise IndexError(f'Index outside the tuple: {index}')

        return self.terms[index-1]
    

    def __str__(self):
        return '{' + ','.join([str(term) for term in self.terms]) + '}'


class Fun():

    def __init__(self, param_type, return_type):
        self.param_type = param_type
        self.return_type = return_type


    def __str__(self):
        return f'(fn({str(self.param_type)})->{str(self.return_type)})'


def compare_types(expected, actual):
    if type(expected) != type(actual):
        return False

    if isinstance(expected, Bool) or isinstance(expected, Nat) or isinstance(expected, Unit):
        return True
    
    if isinstance(expected, Fun):
        return (compare_types(expected.param_type, actual.param_type) and 
                compare_types(expected.return_type, actual.return_type))
    
    if isinstance(expected, Tuple):
        return expected.terms == actual.terms
