
test:
	pytest

version:
	python3 hiquant/version.py bump

package:
	rm dist/*
	python3 setup.py sdist bdist_wheel
	ls -la dist/

publishtest:
	twine upload --repository testpypi dist/* --verbose

publish:
	twine upload --repository pypi dist/* --verbose
