.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/test/ckanext-filtersearch.svg?branch=master
    :target: https://travis-ci.org/test/ckanext-filtersearch

.. image:: https://coveralls.io/repos/test/ckanext-filtersearch/badge.svg
  :target: https://coveralls.io/r/test/ckanext-filtersearch

.. image:: https://pypip.in/download/ckanext-filtersearch/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-filtersearch/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-filtersearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-filtersearch/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-filtersearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-filtersearch/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-filtersearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-filtersearch/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-filtersearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-filtersearch/
    :alt: License

=============
ckanext-filtersearch
=============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!


------------
Requirements
------------

DEFINE: in development.ini/production.ini

 ckanext.filtersearch.topic_field = xxxx

 depends on spatial extension as spatial_query called here

 aöso checks whether spatial extend and time extend have been selected (datesearch)






------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-filtersearch:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-filtersearch Python package into your virtual environment::

     pip install ckanext-filtersearch

3. Add ``filtersearch`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

in development/production.ini:
ckanext.filtersearch.topic_field = iso_tpCat
ckan.extra_resource_fields = par_experiment par_model par_frequency par_variables par_ensemble

(The resource_fields named above need to be present in the json schema file from schemding/mdedit)

schema.xml:
Further more add the following line to schema.xml (best befor dynamic_field entries):
<!-- Change 15-5: -->
  <field name="res_extras_par_experiment" type="string" indexed="true" stored="true" multiValued="true"/>
  <field name="res_extras_par_model" type="string" indexed="true" stored="true" multiValued="true"/>
  <field name="res_extras_par_frequency" type="string" indexed="true" stored="true" multiValued="true"/>
  <field name="res_extras_par_variables" type="string" indexed="true" stored="true" multiValued="true"/>
  <field name="res_extras_par_ensemble" type="string" indexed="true" stored="true" multiValued="true"/>
<!-- Change 15-5 end -->

solr/jetty restart
paster search index rebuild

------------------------
Development Installation
------------------------

To install ckanext-filtersearch for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/test/ckanext-filtersearch.git
    cd ckanext-filtersearch
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.filtersearch --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-filtersearch on PyPI
---------------------------------

ckanext-filtersearch should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-filtersearch. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-filtersearch
----------------------------------------

ckanext-filtersearch is availabe on PyPI as https://pypi.python.org/pypi/ckanext-filtersearch.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
