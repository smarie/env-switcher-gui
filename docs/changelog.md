### 1.3.0 - Popups on error

* Added popups on error so that the GUI provides feedback when an action could not be performed

### 1.2.2 - Packaging fix and improvements

* Fixed packaging for windows: the 'platforms' folder was missing
* Improved the CLI to create sub commands 'apply', 'list' (new) and 'open' (new).
* Added an icon to the app
* The windows installer now creates a shortcut on the desktop
* The CLI is now embedded also in the standalone version, and can be executed from other working directories (solved a Qt import issue)
* Improved documentation

### 1.2.1 - New packaging for releases - both minimal size

* Fixed windows 64 distribution with minimal size so that it is now completely standalone. Reusing independent project [PyQt5-minimal](https://github.com/smarie/PyQt5-minimal)
* Added linux 64 distribution with minimal size, reusing as well [PyQt5-minimal](https://github.com/smarie/PyQt5-minimal) 

### 1.2.0 - New packaging for releases

* Reducing the size of generated distribution on windows and on linux (but on linux it is still quite large as it includes libicudata.so.58, help would be needed to remove this dependency).
* Added licenses for PyQt and Qt
* Now releasing a .tar.gz 'executable' release for linux distributions, and removed the old .tar.gz 'source' file release that was redundant with the github-generated one
* Fixed documentation to include a valid template

### 1.1.0 - Attempt to fix a ghost reference in PyPi 1.0.12

### 1.0.1 - First version with automatic release for Windows 32/64 and PyPi

* Appveyor now deploys the .msi release
* Travis builds the doc and deploys the wheel on PyPi
* Project page contains appropriate documentation to get started

### 1.0.0 - First public working version of envswitcher