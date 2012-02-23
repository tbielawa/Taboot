#!/usr/bin/make

ASCII2MAN = a2x -D $(dir $@) -d manpage -f manpage $<
ASCII2HTMLMAN = a2x -D docs/html/man/ -d manpage -f xhtml
NAME := python-taboot
VERSION := $(shell cat VERSION)
RELEASE := $(shell awk '/Release/{print $$2}' < python-taboot.spec | cut -d "%" -f1)
CURVERSION := $(shell python -c "import taboot; print taboot.__version__")
FULLNAME := $(NAME)-$(VERSION)
MANPAGES := docs/man/man1/taboot.1 docs/man/man5/taboot-tasks.5
DOCPATH := /usr/share/doc/$(NAME)
SITELIB = $(shell python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")
DIST := $(shell rpm --eval "%dist")
RPMNAME := python-taboot-$(VERSION)-$(RELEASE)$(DIST).noarch.rpm
SRPMNAME := python-taboot-$(VERSION)-$(RELEASE)$(DIST).src.rpm

viewdoc: docs
	python ./setup.py viewdoc

docs: manuals htmldocs htmlman

manuals: $(MANPAGES)

%.1: %.1.asciidoc
	$(ASCII2MAN)

%.5: %.5.asciidoc
	$(ASCII2MAN)

htmlman:
	mkdir -p docs/html/man
	$(ASCII2HTMLMAN) docs/man/man1/taboot.1.asciidoc
	$(ASCII2HTMLMAN) docs/man/man5/taboot-tasks.5.asciidoc

htmldocs:
	./setup.py doc

install:
	./setup.py install

installdocs: docs
	mkdir -p /usr/share/doc/$(NAME)
	cp -r docs/rst $(DOCPATH)
	cp -r docs/html $(DOCPATH)
	gzip -c docs/man/man1/taboot.1 > /usr/share/man/man1/taboot.1.gz
	gzip -c docs/man/man5/taboot-tasks.5 > /usr/share/man/man5/taboot-tasks.5.gz

uninstall:
	rm -fR /usr/share/doc/$(NAME)
	rm -f /usr/share/man/man1/taboot.1.gz
	rm -f /usr/share/man/man5/taboot.5.gz
	rm -fR $(SITELIB)/taboot-func/
	rm -fR $(SITELIB)/taboot/
	rm -f /usr/bin/taboot

sdist: clean
	python ./setup.py sdist

# I need to come up with a better way to maintain the version
# information. This next command will fail in interesting ways if
# ./VERSION doesn't match ./taboot/__init__.py's version and the
# version parameter in the spec file.
rpm: clean docs sdist
	mkdir -p rpm-build
	cp dist/*.gz rpm-build/
	rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir  %{_topdir}" \
	-ba python-taboot.spec
	@echo "RPMs have been built and placed in ./rpm-build/"

# Formats the change log entry, increments spec file version, tags this
# release in git.
tag: clean
	tito tag

release:
	@echo $(RELEASE)

version:
	@echo $(VERSION)

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	pep8 taboot/

cleanpy:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

cleanbackup:
	find . -type f -name "*~" -delete
	find . -type f -name "#*" -delete

cleandocs:
	find ./docs/ -type f -name "*.xml" -delete
	rm -fR docs/.doctrees docs/html dist build ./rpm-build

clean: cleanbackup cleanpy cleandocs

.PHONEY: docs manual htmldoc clean version release sdist
vpath %.asciidoc docs/man/man1 docs/man/man5
