# Stella typecheker on Python

[![tests](https://github.com/kolbasaegor/stella-python/actions/workflows/main.yaml/badge.svg)](https://github.com/kolbasaegor/stella-python/actions/workflows/main.yaml)

python>=3.10

antlr4-python3-runtime==4.9.2

## Typecheker support following modules of Stella

+ Core
+ Unit
+ Pairs
+ Tuples
+ Sum
+ Sequencing
+ References
+ Let-binding
+ Errors

## Usage

### how to build?

`pip install -r requirements.txt`

### how to run?

`make` or `make [module name]` (if you want test specific module)

or 

`python src/interpret.py [test_name]`

for example:

+  `python src/interpret.py tests/core/well-typed/factorial.stella`

    output:
    ```
    exit code: 0
    ```

+ `python .\src\interpret.py    tests\core\ill-typed\argument-type-mismatch-3.stella`

    output:
    ```
    RuntimeError: Ill-typed application of function k: expected param type: (fn(Nat)->(fn((fn(Nat)->Bool))->Nat)), actual: (fn(Nat)->(fn((fn(Nat)->Nat))->Nat))
    ```