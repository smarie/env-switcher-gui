#!/bin/bash

# source :
#   http://pyqt.sourceforge.net/Docs/PyQt5/installation.html#building-and-installing-from-source
#   https://wiki.python.org/moin/BuildPyQt4Windows

# before running this script the variable PYQT_DIR and PYQT_VER should exist

echo "***** Starting compilation of PyQt in $PYQT_DIR for installation in python site-packages *******"
export PYQT_VER_MAJOR=${PYQT_VER%.*}
export PYQT_ARCHIVE="PyQt$PYQT_VER_MAJOR_gpl-$PYQT_VER"
export PYQT_SRC_URL="https://sourceforge.net/projects/pyqt/files/PyQt$PYQT_VER_MAJOR/PyQt-$PYQT_VER/$PYQT_ARCHIVE.tar.gz/download"

cd "$TRAVIS_BUILD_DIR/.."
echo "(a) Downloading PyQt sources from $PYQT_SRC_URL in $PWD"
wget -q $PYQT_SRC_URL --no-check-certificate -O $PYQT_ARCHIVE.tar.gz

echo "(b) Unzipping PyQt sources in $PWD"
tar -xvf $PYQT_ARCHIVE.tar.gz >/dev/null
mv $PYQT_ARCHIVE $PYQT_DIR

echo "(c) Installing PyQt dependencies "
# from https://wiki.qt.io/Install_Qt_5_on_Ubuntu: install opengl libraries so as to be able to build QtGui
sudo apt-get install mesa-common-dev
sudo apt-get install libglu1-mesa-dev -y

cd $PYQT_DIR
echo "(d) Patching PyQt configure.py in $PWD"
# apply our HACK patch to fix the generated makefiles
patch ./configure.py < ../ci_tools/pyqt5-configure.py.patch

echo "(e) Configuring PyQt in $PWD"
python configure.py --no-python-dbus --no-qml-plugin --no-qsci-api --no-tools --confirm-license --disable QtHelp --disable QtMultimedia --disable QtMultimediaWidgets --disable QtNetwork --disable QtOpenGL --disable QtPrintSupport --disable QtQml --disable QtQuick --disable QtSql --disable QtSvg --disable QtTest --disable QtWebKit --disable QtWebKitWidgets --disable QtXml --disable QtXmlPatterns --disable QtDesigner --disable QAxContainer --disable QtDBus --disable QtWebSockets --disable QtWebChannel --disable QtNfc --disable QtBluetooth --disable QtX11Extras --disable QtQuickWidgets --disable _QOpenGLFunctions_2_0 --disable _QOpenGLFunctions_2_1 --disable _QOpenGLFunctions_4_1_Core
# --qmake $HOME/miniconda/bin/qmake --sip $HOME/miniconda/bin/sip --verbose

echo "(f) Compiling PyQt in $PWD"
sudo make
