# Stella typecheker on Python

## Usage
how to run?

`make test-well-typed`

`make test-ill-typed`

or 

`python src/interpret.py [test_name].stella`

for example:

`python src/interpret.py tests/well-typed/factorial.stella`

output:
```
Function declaration: Nat2Nat::const
- Actual return type: (fn(Nat)->(fn(Nat)->Nat))
- Expected return type: (fn(Nat)->(fn(Nat)->Nat))

Function declaration: Nat::add
- Actual return type: (fn(Nat)->Nat)
- Expected return type: (fn(Nat)->Nat)

Function declaration: Nat::mul
- Actual return type: (fn(Nat)->Nat)
- Expected return type: (fn(Nat)->Nat)

Function declaration: factorial
- Actual return type: Nat
- Expected return type: Nat

Function declaration: main
- Actual return type: Nat
- Expected return type: Nat

exit code: 0
```
