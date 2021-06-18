
test:
	pytest

version:
	python hiquant/version.py bump

package:
	rm dist/*
	python setup.py sdist bdist_wheel
	ls -la dist/

publishtest:
	twine upload --repository testpypi dist/* --verbose

publish:
	twine upload --repository pypi dist/* --verbose
