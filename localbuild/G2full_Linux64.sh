#=======================================================================
# this creates the gsas2full self-installer for Linux using a git
# repository. 

# based on Jenkins config
#=======================================================================
WORKSPACE=/tmp
gitInstallRepo=git@github.com:GSASII/GSASIIbuildtools.git
gitInstallRepo=https://github.com/GSASII/GSASIIbuildtools.git
# do this in advance so the script can be run 
#rm -rf $WORKSPACE/GSAS2-build
#mkdir $WORKSPACE/GSAS2-build
#git clone $gitInstallRepo $WORKSPACE/GSAS2-build --depth 1
# echo "run this with bash $WORKSPACE/GSAS2-build/install/G2full_Linux64.sh"

condaHome=/tmp/conda311
WORKSPACE=/tmp
builds=/tmp/builds

gitCodeRepo=git@github.com:GSASII/codetest.git
gitCodeRepo=https://github.com/GSASII/codetest.git # needed where ssh does not work

pyver=3.11
numpyver=1.26

packages="python=$pyver wxpython numpy=$numpyver scipy matplotlib pyopengl conda anaconda-client constructor conda-build git gitpython requests pillow h5py imageio scons"


env=bldg2f     # py 3.11.8 & np 12.6.4
#sysType=linux-64
miniforge=https://github.com/conda-forge/miniforge/releases/download/23.11.0-0/Mambaforge-23.11.0-0-Linux-x86_64.sh

install=True
#install=False

dryrun=False
#dryrun=True

gitinstall=True

#build=False
build=True

upload=False

#========== conda stuff
if [ "$install" = "True" ]
then
	if [ ! -e "/tmp/Miniconda3-latest.sh" ]; then
	    curl -L $miniforge -o /tmp/Miniconda3-latest.sh
	else
	    echo "skip miniconda download"
	fi
	if [ ! -d "$condaHome" ]; then
	    bash /tmp/Miniconda3-latest.sh -b -p $condaHome
	else
	    echo "skip miniconda install"
	fi
	#rm /tmp/Miniconda3-latest.sh
fi

echo source $condaHome/bin/activate
     source $condaHome/bin/activate

if [ "$dryrun" = "True" ]
then
    conda create --dry-run -n test-env $packages
    exit
fi

if [ "$install" = "True" ]
then
	conda create -y -n $env $packages
fi

set +x
echo source $condaHome/bin/activate $env
     source $condaHome/bin/activate $env

#=========================== Build of g2complete package ==================================
#
#=============================
# Use commands below to build
#=============================
#if [ "$build" = "True" ]
if [ "$gitinstall" = "True" ]
then
    set -x
    # get the GSAS-II code to get the latest version number etc.
    rm -rf $WORKSPACE/GSAS2-code
    mkdir $WORKSPACE/GSAS2-code
    git clone $gitCodeRepo $WORKSPACE/GSAS2-code --depth 50
fi

if [ "$build" = "True" ]
then    
    echo $WORKSPACE/GSAS2-build/install
    cd   $WORKSPACE/GSAS2-build/install
    echo python `pwd`/setgitversion.py $WORKSPACE/GSAS2-code
    python setgitversion.py $WORKSPACE/GSAS2-code

    
    mkdir -p $builds
    rm -rf $builds/*
    set +x
    echo conda build purge
         conda build purge
    echo conda build purge-all
         conda build purge-all
    echo conda build g2complete --output-folder $builds --numpy $numpyver
         conda build g2complete --output-folder $builds --numpy $numpyver
    set -x
    #ls -ltR $builds
    #cp $builds/osx-64/gsas* /tmp/  # keep the conda package for debugging
    
    #
    #=========================== Build/upload of g2full installer =============================
    #
    # Build the self-installer
    rm -f *.sh
    # constructor g2full
    # March 2024, mamba solver has a problem, fixed in a newer version
    CONDA_SOLVER=classic constructor g2full
    set -x
    echo `pwd`
    ls -l *.sh
    mv -v *.sh ../   # put into $WORKSPACE/GSAS2-build
	#ls -l *.*
fi

exit

if [ "$upload" = "True" ]
then
	echo upload build
	# copy to "Latest" and upload
	#cp gsas2full-*-MacOSX-x86_64.sh gsas2full-Latest-MacOSX-x86_64.sh
	# copy to https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-*-MacOSX-x86_64.sh
	scp ../gsas2full-*.sh svnpgsas@s11bmbcda.xray.aps.anl.gov:/home/joule/SVN/subversion/pyGSAS/downloads/
	#echo files found at https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-*-MacOSX-x86_64.sh
	#ssh svnpgsas@s11bmbcda.xray.aps.anl.gov ls -lt /home/joule/SVN/subversion/pyGSAS/downloads/gsas2full-*-MacOSX-*.sh
fi

