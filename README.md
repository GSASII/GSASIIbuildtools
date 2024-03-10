This repo contains files used for building GSAS-II binaries and
distribution kits from the test git reops found in this organization as well as files for
download.

* gsas2full (directory g2full) creates a standalone installer for GSAS-II, Python and all needed Python 
  packages. Thus it is possible to install GSAS-II from that file even without an internet connection. If one 
  is available, GSAS-II will be updated after installation to the latest available version. 
  Test versions of gsas2full are currently being created for all supported platforms. 

* g2complete (directory g2complete) creates a conda packages that includes all GSAS-II files and the git
  internal files. It is only used to be included inside the gsas2full self-installer. 

The files stored in this repo are probably only of use for GSAS-II developers when packaging GSAS-II. 
The gsas2full installers in the release area will be of general use. The .tgz files in the release area 
are used by the git installer (gitstrap.py) as part of the installation process. 