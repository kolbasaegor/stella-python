class Bool():

    def __init__(self):
        pass


class Nat():

    def __init__(self):
        pass


class Fun():

    def __init__(self, param_type, return_type):
        self.param_type = param_type
        self.return_type = return_type


def compare_types(expected: Bool|Nat|Fun, actual: Bool|Nat|Fun):
    if type(expected) != type(actual):
        return False
    
    if not isinstance(expected, Fun):
        return True
    
    return (compare_types(expected.param_type, actual.param_type) and 
            compare_types(expected.return_type, actual.return_type))
