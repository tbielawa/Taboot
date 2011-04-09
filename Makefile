#!/usr/bin/make

ASCII2MAN = a2x -D $(dir $@) -d manpage -f manpage $<
NAME := python-taboot
VERSION := $(shell cat VERSION)
CURVERSION := $(shell python -c "import taboot; print taboot.__version__")
FULLNAME = $(NAME)-$(VERSION)
MANPAGES := docs/man/man1/taboot.1
DOCPATH := /usr/share/doc/$(NAME)


docs: manuals htmldocs

manuals: $(MANPAGES)

%.1: %.1.asciidoc
	$(ASCII2MAN)

htmldocs:
	./setup.py doc

install: docs
	install docs/rst/ $(DOCPATH)/
	install docs/html/ $(DOCPATH)/
	install docs/man/* $(MANPAGES)/
	./setup.py install

version:
	@echo $(VERSION)

testdist: clean
	tito build --test --tgz

sdist: clean
	@echo "Remember that you should only sdist if you've tagged this release first."
	tito build --tgz

sprm: clean
	@echo "Remember that you shold only srpm if you've tagged this release first."
	tito build --srpm

rpm:
	@echo "Remember that you should only rpm if you've tagged this release first."
	tito builld --rpm

tag: clean
	tito tag

release: clean tag
# Release is a maintainer target. Should handle version bumping,
# source tagging, building docs, creating an sdist for tar.gz
# installs, and building the srpm and rpm (tito will help with a lot
# of this).
	tito build --rpm

testrelease:
# Like a release but in a "build --test" kind of way.
	tito build --test --rpm

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find ./docs/ -type f -name "*.xml" -delete
	find ./docs/ -type f -name "*.1" -delete
	find . -type f -name "#*" -delete
	rm -fR docs/.doctrees docs/html dist build


.PHONEY: docs manual htmldoc clean version release sdist
vpath %.asciidoc docs/man/man1
