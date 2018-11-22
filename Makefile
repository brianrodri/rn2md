init:
	pip install -r requirements.txt

test:
	pylint rn2md tests
	nosetests tests
