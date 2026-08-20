#/***************************************************************************
# CAM
#
# CAM
#							 -------------------
#		begin				: 2025-01-02
#		git sha				: $Format:%H$
#		copyright			: (C) 2025 by Zuhir Benslama
#		email				: zuhirbenslama@protonmail.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 3 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


#Add iso code for any locales you want to support here (space separated)
# default is no locales
LOCALES = ar fr en

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
LRELEASE = lrelease


# translation
SOURCES = \
	__init__.py \
	constants.py

PLUGINNAME = CAM

PY_FILES = \
	__init__.py \
	constants.py

UI_FILES =

EXTRAS = metadata.txt

EXTRA_DIRS = mixins gui layer scripts resources templates data icons i18n style template_data app

COMPILED_RESOURCE_FILES = resources.py

PEP8EXCLUDE=pydev,conf.py,third_party,ui

# QGISDIR points to the location where your plugin should be installed.
# This varies by platform, relative to your HOME directory:
#	* Linux:
#	  .local/share/QGIS/QGIS3/profiles/default/python/plugins/
#	* Mac OS X:
#	  Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
#	* Windows:
#	  AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins'

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	QGISDIR=.local/share/QGIS/QGIS3/profiles/default/python/plugins
endif
ifeq ($(UNAME_S),Darwin)
	QGISDIR=Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
endif
ifdef windir
	QGISDIR=AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins
endif

#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/build/html

PLUGIN_UPLOAD = $(c)/scripts/plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

.PHONY: default
default:
	@echo While you can use make to build and deploy your plugin, pb_tool
	@echo is a much better solution.
	@echo A Python script, pb_tool provides platform independent management of
	@echo your plugins and runs anywhere.
	@echo You can install pb_tool using: pip install pb_tool
	@echo See https://g-sherman.github.io/plugin_build_tool/ for info. 

compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $< || pyside2-rcc -o $*.py $<
	sed -i 's/^from PyQt5 import QtCore/from qgis.PyQt import QtCore/' $*.py

%.qm : %.ts
	$(LRELEASE) $<

test: compile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		python3 -m pytest test/ -v --ignore=test/test_RNA_dialog.py \
		3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

build: compile
	@echo "Build complete."

install: build
	@echo
	@echo "------------------------------------------"
	@echo "Installing plugin to QGIS plugins directory."
	@echo "------------------------------------------"
	rm -rf $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	for dir in $(EXTRA_DIRS); do \
		cp -R $$dir $(HOME)/$(QGISDIR)/$(PLUGINNAME)/; \
	done
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -name '*.pyc' -delete; \
	echo "Plugin installed to $(HOME)/$(QGISDIR)/$(PLUGINNAME)"

deploy: install


# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/$(PLUGINNAME)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR); zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES)

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@chmod +x scripts/compile-strings.sh
	@scripts/compile-strings.sh $(LRELEASE) $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled resource files and pycache"
	@echo "------------------------------------"
	rm -f $(COMPILED_RESOURCE_FILES)
	find . -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name '*.pyc' -delete

doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd help; make html

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --max-line-length=88 --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,W504 --exclude $(PEP8EXCLUDE) . || true
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)
