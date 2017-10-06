#!/bin/bash

# source:
#   https://wiki.qt.io/Install_Qt_5_on_Ubuntu
#   https://wiki.qt.io/Building_Qt_5_from_Git

# before running this script the variable QT_DIR and QT_VER should exist

echo "***** Starting compilation of Qt for installation to $QT_DIR *******"
export QT_VER_SHORT=${QT_VER%.*}
export QT_ARCHIVE="qt-everywhere-opensource-src-$QT_VER"
export QT_SRC_URL="http://download.qt.io/official_releases/qt/$QT_VER_SHORT/$QT_VER/single/$QT_ARCHIVE.tar.xz"
export QT_SRC_DIR="$TRAVIS_BUILD_DIR/../$QT_ARCHIVE"
export QT_PCRE_SRC="$QT_SRC_DIR/qtbase/src/3rdparty/pcre/"

cd "$TRAVIS_BUILD_DIR/.."
echo "(a) Downloading Qt sources from $QT_SRC_URL in $PWD"
wget -q $QT_SRC_URL

echo "(b) Unzipping Qt sources in $PWD/$QT_ARCHIVE"
tar -xvf $QT_ARCHIVE.tar.xz >/dev/null

echo "(c) Installing Qt dependencies "
sudo apt-get install libxcb*
# install opengl libraries so as to be able to build QtGui (from https://wiki.qt.io/Install_Qt_5_on_Ubuntu)
sudo apt-get install mesa-common-dev
sudo apt-get install libglu1-mesa-dev -y

cd $QT_SRC_DIR
echo "(d) Configuring Qt in $PWD"
sudo ./configure -opensource -confirm-license -prefix $QT_DIR -no-icu -no-cups -no-qml-debug -no-compile-examples -no-harfbuzz -no-sql-mysql -no-sql-odbc -no-sql-sqlite -qt-pcre -skip qtlocation -skip qt3d -skip qtmultimedia -skip qtwebchannel -skip qtwayland -skip qtandroidextras -skip qtwebsockets -skip qtconnectivity -skip qtdoc -skip qtwebview -skip qtimageformats -skip qtwebengine -skip qtquickcontrols2 -skip qttranslations -skip qtxmlpatterns -skip qtactiveqt -skip qtx11extras -skip qtsvg -skip qtscript -skip qtserialport -skip qtdeclarative -skip qtgraphicaleffects -skip qtcanvas3d -skip qtmacextras -skip qttools -skip qtwinextras -skip qtsensors -skip qtenginio -skip qtquickcontrols -skip qtserialbus -nomake examples -nomake tests -nomake tools

## Note: to get the list of modules (to use with -skip): find . -regextype sed -maxdepth 1 -regex "./qt[^b^\.].*"
## Note: -no-dbus does not work, it still looks for it later in the compilation
## Fine-tuning: features from this list could be disabled one by one : https://github.com/qt/qtbase/blob/v$QT_VER/src/corelib/global/qfeatures.txt
#-no-feature-TEXTHTMLPARSER -no-feature-TEXTODFWRITER -no-feature-CSSPARSER -no-feature-XMLSTREAM -no-feature-XMLSTREAMREADER -no-feature-XMLSTREAMWRITER -no-feature-DOM -no-feature-TREEWIDGET -no-feature-TABLEWIDGET -no-feature-TEXTBROWSER -no-feature-FONTCOMBOBOX -no-feature-TOOLBAR -no-feature-TOOLBOX -no-feature-GROUPBOX -no-feature-DOCKWIDGET -no-feature-MDIAREA -no-feature-SLIDER -no-feature-SCROLLBAR -no-feature-DIAL -no-feature-SCROLLAREA -no-feature-GRAPHICSVIEW -no-feature-GRAPHICSEFFECT -no-feature-SPINWIDGET -no-feature-TEXTEDIT -no-feature-SYNTAXHIGHLIGHTER -no-feature-RUBBERBAND -no-feature-CALENDARWIDGET -no-feature-PRINTPREVIEWWIDGET -no-feature-FONTDIALOG -no-feature-PRINTDIALOG -no-feature-PRINTPREVIEWDIALOG -no-feature-TABLEVIEW -no-feature-TREEVIEW -no-feature-IMAGEFORMATPLUGIN -no-feature-MOVIE -no-feature-IMAGEFORMAT_BMP -no-feature-IMAGEFORMAT_PPM -no-feature-IMAGEFORMAT_XBM -no-feature-IMAGEFORMAT_XPM -no-feature-IMAGE_HEURISTIC_MASK -no-feature-PICTURE -no-feature-COLORNAMES -no-feature-PRINTER -no-feature-CUPS -no-feature-PAINT_DEBUG -no-feature-FTP -no-feature-HTTP -no-feature-UDPSOCKET -no-feature-NETWORKINTERFACE -no-feature-NETWORKDISKCACHE -no-feature-COMPLETER -no-feature-FSCOMPLETER -no-feature-DESKTOPSERVICES -no-feature-ANIMATION -no-feature-STATEMACHINE

cd $QT_SRC_DIR
echo "(e) Compiling Qt in $PWD - part 1"
sudo make

# we have to build pcre manually BEFORE finishing to compile qt
cd $QT_PCRE_SRC
echo "(f) Building pcre in $PWD"
sudo make
# to test that it works: this command should not say 'not found' : sudo ld -L/usr/src/qt-src/qtbase/lib -lqtpcre

cd $QT_SRC_DIR
echo "(g) Compiling Qt in $PWD - part 2"
sudo make

cd $QT_SRC_DIR
echo "(h) Installing Qt in $QT_DIR from $PWD"
sudo make install

cd "$TRAVIS_BUILD_DIR"
echo "(i) Cleaning up and returning to travid build dir $PWD"
sudo rm -rf $QT_SRC_DIR
