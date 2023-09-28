test-well-typed:
	python src/interpret.py tests/well-typed/factorial.stella
	python src/interpret.py tests/well-typed/increment_twice.stella
	python src/interpret.py tests/well-typed/logical-operators.stella
	python src/interpret.py tests/well-typed/squares.stella

test-ill-typed:
	python src/interpret.py tests/ill-typed/bad-squares-1.stella
	python src/interpret.py tests/ill-typed/bad-squares-2.stella
	