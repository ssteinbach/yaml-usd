all:
	@python -m unittest discover
	./bad_usdcat.py test.yml.usda
