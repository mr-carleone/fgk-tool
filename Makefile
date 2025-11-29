.PHONY: install test clean

install:
	pip install -e .

test:
	python -m tests.test_fgk

clean:
	rm -f *.fgk *.txt *.decoded
