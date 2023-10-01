# Stella typecheker on Python
python==3.11.5

antlr4-python3-runtime==4.9.2

## Usage

### how to build?

`pip install -r requirements.txt`

### how to run?

`make mytest`

or 

`python src/interpret.py [test_name]`

for example:

`python src/interpret.py tests/core/well-typed/factorial.stella`

output:
```
exit code: 0
```

`python .\src\interpret.py tests\core\ill-typed\argument-type-mismatch-3.stella`

output:
```
RuntimeError: Ill-typed application of function k: expected param type: (fn(Nat)->(fn((fn(Nat)->Bool))->Nat)), actual: (fn(Nat)->(fn((fn(Nat)->Nat))->Nat))
```