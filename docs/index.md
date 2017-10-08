# envswitch

[![Windows Build](https://ci.appveyor.com/api/projects/status/15y7mvbqi4qu2v4y?svg=true)](https://ci.appveyor.com/project/smarie/env-switcher-gui) [![Linux build](https://travis-ci.org/smarie/env-switcher-gui.svg?branch=master)](https://travis-ci.org/smarie/env-switcher-gui) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/env-switcher-gui/) [![PyPI](https://img.shields.io/badge/PyPI-envswitch-blue.svg)](https://pypi.python.org/pypi/envswitch/)

`envswitch` provides a very simple GUI and CLI to easily switch between environments. 

![ScreenCap](./Example.png)

A typical use case is when you sometimes work behind a network proxy and sometimes not: you have to often change the values of your `http_proxy`, `https_proxy`, `no_proxy` and `curl_ca_bundle` environment variables as explained [here](https://github.com/smarie/develop-behind-proxy). 

`envswitch` provides you with a very convenient way to remember **sets of environment variables** with associated values, and to apply a given set (so-called 'environment') at any time in a mouse click or a terminal command. 

In addition, `envswitch` allows users to save environment definition files as `.yaml`, so as to ease the process of sharing such files among developers.


## Standalone desktop app

### Install envswitch app

You may install the envswitch app using the installers provided in the [releases](https://github.com/smarie/env-switcher-gui/releases/) page.

### Launch envswitch app

Once the standalone app is installed, you simply have to launch the executable file (`envswitch.exe` on windows, `envswitch` on linux). 

## For python developers: envswitch wheel

### Prerequisite: install PyQt

If you are using conda, it is recommended that you rely on `conda` to install `pyqt` rather than on `pip`:

```bash
> conda install pyqt>=5.6
```

Actually the above is **REALLY** recommended on Anaconda, as using pip to install pyqt in anaconda root may compromise your global conda environment (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/1970)). 

If you are not an Anaconda user then you have to manually install PyQt, since it is not included in the package dependencies in order to avoid the above to happen: 

```bash
> pip install pyqt5
```

### Install envswitch wheel

Then,simply install as usual with pip:

```bash
> pip install envswitch
```

### Launch envswitch from terminal

`envswitch` installs the following commandline entry points in your terminal:

* `envswitch_gui` launches the GUI detached from the terminal
* `envswitch_gui_debug` launches the GUI attached to the terminal. This allows to see the execution logs and potential error messages.
* `envswitch` is the commandline entrypoint. Use `envswitch --help` for details

## Example usage

### Configuration file

A `.yml` or `.yaml` configuration file is needed to use the tool. The format is really simple: it is a yaml file containing a list of named environments (`env_a` and `env_b` below), where each environment contains a list of environment variable names and values:

```yaml
env_a:
  name: Hello
  foo: 'hello'
  bar: 'world'

env_b:
  name: Goodbye
  foo: 'goodbye'
  bar: 'world'
```

An optional special variable named 'name', can be provided in order to customize the name of the environment in the GUI. Note that you can provide any number of environments, and they do not necessarily have to contain the same variables.

Here is a [template file](network_config.yml) for network configuration, to switch between proxy and no proxy states (see [here](https://github.com/smarie/develop-behind-proxy) for details).

### GUI

The following screen capture shows the GUI loaded with a network proxy switching configuration file. 

![ScreenCap](./Example.png)

* Two environments are defined: "No proxy" and "Proxy" 
* The user may select the one to apply by clicking on the corresponding tab, and by clicking on the 'Apply' button. This will set all of the defined environment variables to their displayed values.

### CLI

The commandline version of envswitch provides an easy way to switch between environments. Instead of opening the GUI, clicking on the 'No proxy' tab and clicking on 'Apply', you may simply do it in the terminal:

```bash
> envswitch no_proxy
``` 

Note that by default the configuration file used will be the last one edited with the GUI. If you wish to use another one, simply specify it with the `-f` option:

```bash
> envswitch -f other_config.yml other_env_id
```


## See Also

Inspiring references:

* Python desktop apps Overview: [http://takluyver.github.io/posts/so-you-want-to-write-a-desktop-app-in-python.html](http://takluyver.github.io/posts/so-you-want-to-write-a-desktop-app-in-python.html)
* PyQt and Qt designer: [https://nikolak.com/pyqt-qt-designer-getting-started/](https://nikolak.com/pyqt-qt-designer-getting-started/)
* PyQt Main Window example: [http://doc.qt.io/qt-5/qtwidgets-mainwindows-application-example.html](http://doc.qt.io/qt-5/qtwidgets-mainwindows-application-example.html)
* Resources in Qt: [https://stackoverflow.com/questions/36673900/importing-resource-file-to-pyqt-code](https://stackoverflow.com/questions/36673900/importing-resource-file-to-pyqt-code)
* Example project with tray icon: [https://github.com/dglent/meteo-qt](https://github.com/dglent/meteo-qt)
* MVC with PyQt: 
    * [https://stackoverflow.com/questions/1660474/pyqt-and-mvc-pattern](https://stackoverflow.com/questions/1660474/pyqt-and-mvc-pattern)
    * (in french) [https://openclassrooms.com/courses/programmez-avec-le-langage-c/l-architecture-mvc-avec-les-widgets-complexes](https://openclassrooms.com/courses/programmez-avec-le-langage-c/l-architecture-mvc-avec-les-widgets-complexes)

Alternatives to PyQt: 
* [Enaml](http://nucleic.github.io/enaml/docs/index.html)
* [wxPython](http://zetcode.com/wxpython/introduction/)

Alternatives to cx_Freeze:
* [pyinstaller](https://github.com/pyinstaller/pyinstaller/wiki), with this [tutorial](http://www.blog.pythonlibrary.org/2010/08/10/a-pyinstaller-tutorial-build-a-binary-series/)

*Do you like this project ? You might also like [these](https://github.com/smarie?utf8=%E2%9C%93&tab=repositories&q=&type=&language=python)* 


## Want to contribute ?

Details on the github page: [https://github.com/smarie/env-switcher-gui](https://github.com/smarie/env-switcher-gui)
