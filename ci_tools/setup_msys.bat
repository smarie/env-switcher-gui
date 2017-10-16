SET "PATH=%MSYS2_DIR%\%MSYSTEM%\bin;%MSYS2_DIR%\usr\bin;%PATH%"

echo "Setup MSYS2 for Qt build (see https://wiki.qt.io/MSYS2)"

echo "-- First update msys2 core components"
bash -lc "pacman -Sy --noconfirm"
bash -lc "pacman --needed --noconfirm -S bash pacman pacman-mirrors msys2-runtime"

echo "-- Then update the rest of other components"
bash -lc "pacman -Su --noconfirm"

echo "-- load MinGW-w64 SEH (64bit/x86_64) posix and Dwarf-2 (32bit/i686) posix toolchains & related other tools, dependencies & components from MSYS2 REPO"
bash -lc "pacman -S --needed --noconfirm base-devel git mercurial cvs wget p7zip"
bash -lc "pacman -S --needed --noconfirm perl ruby python2 mingw-w64-i686-toolchain mingw-w64-x86_64-toolchain"

cd %APPVEYOR_BUILD_FOLDER%

REM echo "-- installing jom"
REM appveyor DownloadFile "http://download.qt.io/official_releases/jom/jom.zip"
REM 7z x jom.zip -o%APPVEYOR_BUILD_FOLDER%\jom > nul