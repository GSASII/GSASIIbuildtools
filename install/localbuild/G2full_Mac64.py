#=======================================================================
# this creates the gsas2full self-installer for Mac using a git
# repository. 

# based on Jenkins config
#=======================================================================
#which gfortran
#find /usr/local -name "libquadmath*dylib" -print
#find /usr/local -name "libgcc*dylib" -print
condaHome=/tmp/conda311
env=py311     # py 3.11.8 & np 12.6.4
sysType=osx-64
miniforge=https://github.com/conda-forge/miniforge/releases/download/23.11.0-0/Mambaforge-23.11.0-0-MacOSX-x86_64.sh

install=True
install=False

#compile=True
compile=False
build=False
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
    conda create --dry-run -n test python=3.11 wxpython numpy scipy matplotlib pyopengl conda anaconda-client constructor conda-build # requests pillow h5py imageio scons 
    exit
fi

if [ "$install" = "True" ]
then
	conda create -y -n $env python=3.11 wxpython numpy scipy matplotlib pyopengl conda anaconda-client constructor conda-build # requests pillow h5py imageio scons 
fi

set +x
echo 'source $condaHome/bin/activate $env'
      source $condaHome/bin/activate $env

conda install -y conda anaconda-client constructor conda-build 
exit
#==================================== Build of .so files ==================================
if [ "$compile" = "True" ]
then
  #ls -l  $CONDA_PREFIX/bin/*gfortran
  # gfortran seems to be setup by conda
  #ln -sf $CONDA_PREFIX/bin/x86_64-conda_cos6-linux-gnu-gfortran $CONDA_PREFIX/bin/gfortran
  #=======================
  # get source code
  #=======================
  #rm -rf $WORKSPACE/GSASII
  #mkdir -p $WORKSPACE/GSASII
  $svn co https://subversion.xray.aps.anl.gov/pyGSAS/trunk/fsource $WORKSPACE/GSASII/fsource
  ########################
  # start compile process
  ########################
  # START debug stuff
  set -x
  which python
  #gfortran -v
  #   which ld
  #export PATH="/usr/local/bin:$PATH"  # make sure system gfortran is used
  export FORTpath="/usr/local/bin"
  which $FORTpath/gfortran
  export FLIBloc="/usr/local/opt/gcc/lib/gcc/current/"
  rm -rf GSASII/AllBinaries
  cd $WORKSPACE/GSASII/fsource

  scons -c # cleanup old
  set +x
  scons install=T FORTpath=$FORTpath LIBGFORTRAN=T LIBGCC=T # LIBGFORTRAN seems OK on OSX
  # document build
  #=# find the build dir name; add info to Build notes
  newdir=`cd ../AllBinaries/; ls -d mac*`
  echo $newdir
  set -x
  cp ../bin/Build.notes.txt ../AllBinaries/$newdir/
  echo "Built with Jeeves from $JOB_NAME from G2 version $SVN_REVISION on $NODE_LABELS" >> ../AllBinaries/$newdir/Build.notes.txt
  sw_vers >> ../AllBinaries/$newdir/Build.notes.txt
  conda list -f python | tail -1 >> ../AllBinaries/$newdir/Build.notes.txt
  conda list -f numpy | tail -1 >> ../AllBinaries/$newdir/Build.notes.txt
  #conda list -f gfortran_linux-64 | tail -1 >> ../AllBinaries/$newdir/Build.notes.txt
  echo "Using $FORTpath/gfortran (info follows)" >> ../AllBinaries/$newdir/Build.notes.txt
  $FORTpath/gfortran -v 2>> ../AllBinaries/$newdir/Build.notes.txt
  #================
  # Upload binaries
  #================
  $svn co -q https://subversion.xray.aps.anl.gov/pyGSAS/Binaries $WORKSPACE/Binaries
fi

if [[ ("$compile" = "True") && (! -d $WORKSPACE/Binaries/$newdir) ]]
then
    mkdir $WORKSPACE/Binaries/$newdir
    $svn add $WORKSPACE/Binaries/$newdir
fi

if [ "$compile" = "True" ]
then
  python $WORKSPACE/Binaries/macRelink.py ../AllBinaries/$newdir
  cp ../AllBinaries/$newdir/* $WORKSPACE/Binaries/$newdir
  #cp $CONDA_PREFIX/lib/libgcc_s.1.dylib $WORKSPACE/Binaries/$newdir/
  cp $FLIBloc/libquadmath.0.dylib $WORKSPACE/Binaries/$newdir/
  echo Uploading
  $svn add --force $WORKSPACE/Binaries/$newdir/*
  $svn st $WORKSPACE/Binaries
  $svn ci -m"Build with $JOB_NAME on $NODE_LABELS" --username svnjenkins --password $JENKINS_PASS  --non-interactive $WORKSPACE/Binaries
fi
#
#=========================== Build of g2complete package ==================================
#
#=============================
# Use commands below to build
#=============================
if [ "$build" = "True" ]
then
    set -x
    cd $WORKSPACE/GSAS-II/install
    export PATH=$WORKSPACE/GSAS-II/install/svn/anaconda_mac64/bin:$PATH
	python setversion.py
	mkdir -p ~/builds
	rm -rf ~/builds/*
	set +x
	echo conda build purge
    	 conda build purge
	echo conda build g2complete --output-folder ~/builds
    	     conda build g2complete --output-folder ~/builds
	set -x
    #ls -ltR ~/builds
    cp ~/builds/osx-64/gsas* ./  # keep the conda package for debugging
	#
	#=========================== Build/upload of g2full installer =============================
	#
	# Build the self-installer
	rm -f *.sh
	constructor g2full
	set -x
	ls -l *.sh
	#ls -l *.*
fi

if [ "$upload" = "True" ]
then
	echo upload build
	# copy to "Latest" and upload
	#cp gsas2full-*-MacOSX-x86_64.sh gsas2full-Latest-MacOSX-x86_64.sh
	# copy to https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-*-MacOSX-x86_64.sh
	scp gsas2full-*.sh svnpgsas@s11bmbcda.xray.aps.anl.gov:/home/joule/SVN/subversion/pyGSAS/downloads/
	#echo files found at https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-*-MacOSX-x86_64.sh
	#ssh svnpgsas@s11bmbcda.xray.aps.anl.gov ls -lt /home/joule/SVN/subversion/pyGSAS/downloads/gsas2full-*-MacOSX-*.sh
fi
