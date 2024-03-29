# this is used during the gsas2full (& gsas2complete) build process
# to modify the g2complete & g2full .template files to reflect the
# versions of Python & packages that should be used for builds. 
#

import os
import sys
import platform
#import datetime as dt
import git
import numpy as np
import wx
import matplotlib as mpl
import platform

if len(sys.argv) < 2:
    G2code = os.path.join(os.path.dirname(__file__),'GSAS2-code')
    raise Exception('setgitversion broken with only one arg')
else:
    G2code = os.path.abspath(sys.argv[1])
if not os.path.exists(G2code):
    print(f'Path to GSAS-II code {G2code} not found')
    sys.exit()
print(f'GSAS-II code: {G2code}')
try:
    g2repo = git.Repo(G2code)
except:
    print('Launch of gitpython for version file failed'+
              f' with path {G2code}')
    sys.exit()
commit = g2repo.head.commit
ctim = commit.committed_datetime.strftime('%H:%M %d-%b-%Y')
commit0 = commit.hexsha
for i in g2repo.iter_commits('HEAD'): # get a numeric tag for the last commit
    tags = [t for t in g2repo.git.tag('--points-at',i).split('\n') if t.isnumeric()]
    print(i,tags)
    if tags:
        G2version = tags[0]
        break
else:
    G2version = '?' # no tag in history

npversion = np.__version__[:np.__version__.find('.',2)]
#wxversion = wx.__version__[:wx.__version__.find('.',2)]
wxversion = wx.__version__
mplversion = mpl.__version__[:mpl.__version__.find('.',2)]
pyversion = platform.python_version()
if pyversion.find('.',2) > 0: pyversion = pyversion[:pyversion.find('.',2)]
print ('GSAS-II version   {}'.format(G2version))
print ('python version is {}'.format(pyversion))
print ('numpy version is  {}'.format(npversion))
print ('wx version is     {}'.format(wxversion))
print ('MPL version is    {}'.format(mplversion))

for fil in ('g2complete/meta.yaml','g2complete/build.sh',
                'g2complete/bld.bat',
                'g2full/construct.yaml',
                'g2full/g2postinstall.bat',
                'g2full/g2postinstall.sh',
                ):
    try:
        note = ''
        if platform.machine() == 'aarch64' and os.path.exists(fil+'.Pitemplate'): # Raspberry Pi
            fp = open(fil+'.Pitemplate','r')
        else:
            fp = open(fil+'.template','r')
        out = fp.read().replace('**Version**',G2version)
        fp.close()
    except FileNotFoundError:
        print('Skipping ',fil)
        continue
    if sys.platform == "win32" and platform.architecture()[0] != '64bit':
        if 'win-64' in out:
            print('changing for 32-bit windows')
            out = out.replace('win-64','win-32')
    if sys.platform.startswith("linux") and platform.architecture()[0] != '64bit':
        if 'linux-64' in out:
            print('changing for 32-bit linux')
            out = out.replace('linux-64','linux-32')
    out = out.replace('**pyversion**',pyversion)
    out = out.replace('**npversion**',npversion)
    out = out.replace('**wxversion**',wxversion)
    out = out.replace('**mplversion**',mplversion)
    if sys.platform == "darwin": out.replace('#MACOnly#','')
    if platform.machine() == 'aarch64' and 'meta' in fil: # Raspberry Pi
        out = out.replace('- wxpython=','# - wxpython=')
        note = 'customized for Raspberry Pi OS'
    elif (platform.machine() == 'arm64' and sys.platform == "darwin"
            and 'construct' in fil): # MacOS-arm64
        out = out.replace('- /tmp/builds/osx-64','#- /tmp/builds/osx-64')
        out = out.replace('[osx-arm64]','[osx]')
        note = 'customized for MacOS-arm64'
    elif sys.platform == "darwin" and 'construct' in fil: # MacOS-arm64
        out = out.replace('- /tmp/builds/osx-arm64','#- /tmp/builds/osx-arm64')
        out = out.replace('[osx-64]','[osx]')
        note = 'customized for MacOS-x86-64'
    elif sys.platform == "win32" and 'construct' in fil: # Windows, remove OSX lines
        out = out.replace('- /tmp/builds/osx','#- /tmp/builds/osx')
        note = 'customized for Win-64'
    elif sys.platform.startswith("linux"):
        out = out.replace('- /tmp/builds/osx','#- /tmp/builds/osx')
        note = 'customized for Linux-64'
    print('Creating',fil,note)
    fp = open(fil,'w')
    fp.write(out)
    fp.close()
    
