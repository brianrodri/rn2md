init:
	python3 -m pip install -r requirements.txt

test:
	nosetests tests

install:
	python3 -m pip install . --user

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
