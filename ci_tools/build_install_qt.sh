#!/bin/bash

# before running this script the variable QT_DIR should exist.
echo "***** Starting compilation of Qt for installation to $QT_DIR *******"
export QT_SRC_DIR="$TRAVIS_BUILD_DIR/../qt-everywhere-opensource-src-5.6.3"
export QT_SRC_URL="http://download.qt.io/official_releases/qt/5.6/5.6.3/single/qt-everywhere-opensource-src-5.6.3.tar.xz"

echo "(a) Downloading Qt sources from $QT_SRC_URL in "
pwd
wget -q $QT_SRC_URL

echo "(b) Unzipping Qt5.6 sources in "
pwd
tar -xvf qt-everywhere-opensource-src-5.6.3.tar.xz >/dev/null

echo "(c) Installing Qt dependencies "
sudo apt-get install libxcb*
# from https://wiki.qt.io/Install_Qt_5_on_Ubuntu: install opengl libraries so as to be able to build QtGui
sudo apt-get install mesa-common-dev
sudo apt-get install libglu1-mesa-dev -y

echo "(d) Configuring Qt"
cd $QT_SRC_DIR
pwd
sudo ./configure -opensource -confirm-license -prefix $QT_DIR -no-icu -no-cups -no-harfbuzz -skip qtlocation -skip qt3d -skip qtmultimedia -skip qtwebchannel -skip qtwayland -skip qtandroidextras -skip qtwebsockets -skip qtconnectivity -skip qtdoc -skip qtwebview -skip qtimageformats -skip qtwebengine -skip qtquickcontrols2 -skip qttranslations -skip qtxmlpatterns -skip qtactiveqt -skip qtx11extras -skip qtsvg -skip qtscript -skip qtserialport -skip qtdeclarative -skip qtgraphicaleffects -skip qtcanvas3d -skip qtmacextras -skip qttools -skip qtwinextras -skip qtsensors -skip qtenginio -skip qtquickcontrols -skip qtserialbus

## Note: to get the list of modules (to use with -skip): find . -regextype sed -maxdepth 1 -regex "./qt[^b^\.].*"
## Note: -no-dbus does not work, it still looks for it later in the compilation
## Fine-tuning: features from this list could be disabled one by one : https://github.com/qt/qtbase/blob/v5.6.3/src/corelib/global/qfeatures.txt
#-no-feature-TEXTHTMLPARSER -no-feature-TEXTODFWRITER -no-feature-CSSPARSER -no-feature-XMLSTREAM -no-feature-XMLSTREAMREADER -no-feature-XMLSTREAMWRITER -no-feature-DOM -no-feature-TREEWIDGET -no-feature-TABLEWIDGET -no-feature-TEXTBROWSER -no-feature-FONTCOMBOBOX -no-feature-TOOLBAR -no-feature-TOOLBOX -no-feature-GROUPBOX -no-feature-DOCKWIDGET -no-feature-MDIAREA -no-feature-SLIDER -no-feature-SCROLLBAR -no-feature-DIAL -no-feature-SCROLLAREA -no-feature-GRAPHICSVIEW -no-feature-GRAPHICSEFFECT -no-feature-SPINWIDGET -no-feature-TEXTEDIT -no-feature-SYNTAXHIGHLIGHTER -no-feature-RUBBERBAND -no-feature-CALENDARWIDGET -no-feature-PRINTPREVIEWWIDGET -no-feature-FONTDIALOG -no-feature-PRINTDIALOG -no-feature-PRINTPREVIEWDIALOG -no-feature-TABLEVIEW -no-feature-TREEVIEW -no-feature-IMAGEFORMATPLUGIN -no-feature-MOVIE -no-feature-IMAGEFORMAT_BMP -no-feature-IMAGEFORMAT_PPM -no-feature-IMAGEFORMAT_XBM -no-feature-IMAGEFORMAT_XPM -no-feature-IMAGE_HEURISTIC_MASK -no-feature-PICTURE -no-feature-COLORNAMES -no-feature-PRINTER -no-feature-CUPS -no-feature-PAINT_DEBUG -no-feature-FTP -no-feature-HTTP -no-feature-UDPSOCKET -no-feature-NETWORKINTERFACE -no-feature-NETWORKDISKCACHE -no-feature-COMPLETER -no-feature-FSCOMPLETER -no-feature-DESKTOPSERVICES -no-feature-ANIMATION -no-feature-STATEMACHINE

echo "(e) Building pcre "
# we have to build pcre manually BEFORE compiling qt
cd $QT_SRC_DIR/qtbase/src/3rdparty/pcre/
pwd
sudo make
# test that it works: this command should not say 'not found' : sudo ld -L/usr/src/qt-everywhere-opensource-src-5.6.3/qtbase/lib -lqtpcre


echo "(f) Compiling and installing Qt"
cd $QT_SRC_DIR
pwd
make install


echo "(g) Cleaning up and returning to travid build dir"
cd "$TRAVIS_BUILD_DIR"
pwd
rm -rf $QT_SRC_DIR
