#!/bin/bash

wget -q https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.6/PyQt5_gpl-5.6.tar.gz/download --no-check-certificate
tar -xvf download >/dev/null

# from https://wiki.qt.io/Install_Qt_5_on_Ubuntu: install opengl libraries so as to be able to build QtGui
sudo apt-get install mesa-common-dev
sudo apt-get install libglu1-mesa-dev -y

cd PyQt5_gpl-5.6/

# apply our HACK patch to fix the generated makefiles
patch ./configure.py < ../ci_tools/pyqt5-configure.py.patch

# compile
python configure.py --no-python-dbus --no-qml-plugin --no-qsci-api --no-tools --confirm-license --disable QtHelp --disable QtMultimedia --disable QtMultimediaWidgets --disable QtNetwork --disable QtOpenGL --disable QtPrintSupport --disable QtQml --disable QtQuick --disable QtSql --disable QtSvg --disable QtTest --disable QtWebKit --disable QtWebKitWidgets --disable QtXml --disable QtXmlPatterns --disable QtDesigner --disable QAxContainer --disable QtDBus --disable QtWebSockets --disable QtWebChannel --disable QtNfc --disable QtBluetooth --disable QtX11Extras --disable QtQuickWidgets --disable _QOpenGLFunctions_2_0 --disable _QOpenGLFunctions_2_1 --disable _QOpenGLFunctions_4_1_Core
# --qmake $HOME/miniconda/bin/qmake --sip $HOME/miniconda/bin/sip --verbose

make
