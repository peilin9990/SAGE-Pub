sync:
	python sync_readme.py

serve: sync
	mkdocs serve

build: sync
	mkdocs build
