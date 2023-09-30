# Stella typecheker on Python
python>=3.10

## Usage
how to run?

`make mytest`

or 

`python src/interpret.py [test_name]`

for example:

`python src/interpret.py tests/core/well-typed/factorial.stella`

output:
```
exit code: 0
```

`python .\src\interpret.py .\tests\core\ill-typed\bad-squares-1.stella`

output:
```
RuntimeError: Ill-typed function Nat::add: expected return type: <stypes.Nat object at 0x000001CBD4702390>, actual: <stypes.Fun object at 0x000001CBD4740910>
```