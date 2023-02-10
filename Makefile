project := fastapi_opentracing
flake8 := flake8
pytest := pytest

.PHONY: bootstrap
bootstrap:
	pip install -r requirements.txt
	pip install -r requirements-tests.txt
	python setup.py develop

.PHONY: test
test:
	$(pytest)

.PHONY: lint
lint:
	$(flake8) $(project)

.PHONY: clean
clean:
	rm -r build dist fastapi_opentracing.egg-info