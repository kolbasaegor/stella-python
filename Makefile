all: test

test: test-core test-exceptions test-let test-pairs test-references test-sequencing test-sum-types test-tuples

test-core:
	python src/interpret.py tests/core/well-typed/factorial.stella
	python src/interpret.py tests/core/well-typed/higher-order-1.stella
	python src/interpret.py tests/core/well-typed/increment_twice.stella
	python src/interpret.py tests/core/well-typed/logical-operators.stella
	python src/interpret.py tests/core/well-typed/squares.stella 

test-exceptions:
	python src/interpret.py tests/exceptions/well-typed/panic-1.stella
	python src/interpret.py tests/exceptions/well-typed/panic-2.stella
	python src/interpret.py tests/exceptions/well-typed/panic-3.stella

test-let:
	python src/interpret.py tests/let/well-typed/let-1.stella
	python src/interpret.py tests/let/well-typed/let-2.stella

test-pairs:
	python src/interpret.py tests/pairs/well-typed/pairs-1.stella
	python src/interpret.py tests/pairs/well-typed/pairs-2.stella

test-references:
	python src/interpret.py tests/references/well-typed/refs-1.stella
	python src/interpret.py tests/references/well-typed/refs-2.stella
	python src/interpret.py tests/references/well-typed/refs-4.stella

test-sequencing:
	python src/interpret.py tests/sequencing/well-typed/s1.stella

test-sum-types:
	python src/interpret.py tests/sum-types/well-typed/simple-match.stella
	python src/interpret.py tests/sum-types/well-typed/sum-types-1.stella
	python src/interpret.py tests/sum-types/well-typed/sum-types-1.stella

test-tuples:
	python src/interpret.py tests/tuples/well-typed/tuples-1.stella

test-records:
	python src/interpret.py tests/records/well-typed/records-1.stella



run:
	python src/interpret.py tests/mytests/a.stella