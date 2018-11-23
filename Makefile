init:
	pip install -r requirements.txt

test:
	nosetests tests

install:
	python3 setup.py install

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
