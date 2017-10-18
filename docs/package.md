# For python developers: envswitch wheel

## Installation

### Prerequisite: PyQt

If you use conda for your python distribution, it is recommended that you rely on `conda` to install `pyqt` rather than on `pip`:

```bash
> conda install pyqt>=5.6
```

Actually the above is **REALLY** recommended on Anaconda, as using pip to install pyqt in anaconda root may compromise your global conda environment (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/1970)). 

If you are not an Anaconda user then you have to manually install PyQt, since it is not included in the package dependencies in order to avoid the above to happen: 

```bash
> pip install pyqt5
```

Alternatively for linux x64, you may wish to install this [minimal version](https://github.com/smarie/PyQt5-minimal), that is sufficient for envswitch to run.


### Install envswitch wheel

Simply install as usual with pip:

```bash
> pip install envswitch
```


## Usage

`envswitch` installs the following commandline entry points in your python terminal:

* `envswitch_gui` launches the GUI detached from the terminal. See [standalone app](./standalone) section for more details
* `envswitch_gui_debug` launches the GUI attached to the terminal. This allows users to see the execution logs and potential error messages.
* `envswitch` is the commandline entrypoint.

See [Usage](./index#usage) for details