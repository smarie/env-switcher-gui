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