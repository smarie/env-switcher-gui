# env-switcher-gui

[![Windows Build](https://ci.appveyor.com/api/projects/status/15y7mvbqi4qu2v4y?svg=true)](https://ci.appveyor.com/project/smarie/env-switcher-gui) [![Linux build](https://travis-ci.org/smarie/env-switcher-gui.svg?branch=master)](https://travis-ci.org/smarie/env-switcher-gui) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/env-switcher-gui/) [![PyPI](https://img.shields.io/badge/PyPI-envswitch-blue.svg)](https://pypi.python.org/pypi/envswitch/)

A very simple GUI and CLI to manage environment variables.


Project page : [https://smarie.github.io/env-switcher-gui/](https://smarie.github.io/env-switcher-gui/)

## Developer memo for QtDesigner 

### Architecture 
 
This is a kind of MVC pattern where 

* the **View** is made of two parts: the static one `UI_MainWindow`, generated with qt designer, and the dynamic one `EnvSwitcherView`. It deals with the various widgets and popups.
* the **Model** is provided by `EnvSwitcherState` and deals with the configuration files and persistence.
* the **Controller**, or the **Application**, is provided by `EnvSwitcherApp` and provides the Qt application boilerplate as well as persistence of the application settings (recent edited files).


[![EnvswitchDesign](https://raw.githubusercontent.com/smarie/env-switcher-gui/master/docs/DesignOverview.png)](https://raw.githubusercontent.com/smarie/env-switcher-gui/master/docs/DesignOverview.png)


### PyQt Code generation

*Prerequisite: install PyQt5, but warning: using pip to install pyqt in anaconda root may compromise your global conda environment (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/1970))*
* Run `designer`, save file as `*.ui` for example we use `./ui/sprint2_dynamic.ui`
* Generate equivalent python file with `pyuic5 ui/sprint2_dynamic.ui -o envswitch/qt_design.py`


## Want to contribute ?

Contributions are welcome ! Simply fork this project on github, commit your contributions, and create pull requests.

Here is a non-exhaustive list of interesting open topics: [https://github.com/smarie/env-switcher-gui/issues](https://github.com/smarie/env-switcher-gui/issues)


## Running the tests

This project uses `pytest`. 

```bash
pytest -v envswitch/tests/
```

You may need to install requirements for tests beforehand, using 

```bash
pip install -r ci_tools/requirements-test.txt
```

## Packaging

### Python wheel

This project uses `setuptools_scm` to synchronise the version number. Therefore the following command should be used for development snapshots as well as official releases: 

```bash
python setup.py egg_info bdist_wheel rotate -m.whl -k3
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-setup.txt
```

### Standalone app

To build the executable distribution there is a separate setup file for cx_freeze.

The following command builds a distribution folder under `build/` containing all resources needed and an envswitch executable for you platform. 

```bash
python setup_cx_app.py build
```

The following command builds a .msi distribution for windows in `dist/`

```bash
python setup_cx_app.py bdist_msi
```

The following command builds a RPM distribution for linux in `dist/`

```bash
python setup_cx_app.py bdist_rpm
```

The following command builds a .app distribution for mac in `dist/`

```bash
python setup_cx_app.py bdist_mac
```

The following command builds a DMG disk image distribution for mac

```bash
python setup_cx_app.py bdist_dmg
```


## Generating the documentation page

This project uses `mkdocs` to generate its documentation page. Therefore building a local copy of the doc page may be done using:

```bash
mkdocs build
```

You may need to install requirements for doc beforehand, using 

```bash
pip install -r ci_tools/requirements-doc.txt
```

## Generating the test reports

The following commands generate the html test report and the associated badge. 
Note that in order for the test to succeed, you should create an environment variable named 'FOO' beforehand, with random content.

```bash
pytest --junitxml=junit.xml -v envswitch/tests/
ant -f ci_tools/generate-junit-html.xml
python ci_tools/generate-junit-badge.py
```

### PyPI Releasing memo

This project is now automatically deployed to PyPI by Travis when a tag is created. Anyway, for manual deployment we can use:

```bash
twine upload dist/* -r pypitest
twine upload dist/*
```
