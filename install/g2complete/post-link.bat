set logfile=%PREFIX%\g2complete_postlink.log
echo Preparing to install GSAS-II from GitHub > %logfile%
REM create bootstrap batch file ================================================
echo REM Commands to run GSAS-II load/update process > "%PREFIX%\start_G2_bootstrap.bat"
echo call %PREFIX%\Scripts\activate >> "%PREFIX%\start_G2_bootstrap.bat"
echo python %PREFIX%\gitstrap.py >> "%PREFIX%\start_G2_bootstrap.bat"
REM create shortcut to start GSAS-II     =======================================
echo REM Commands to run GSAS-II load/update process > "%PREFIX%\start_GSASII.bat"
echo call %PREFIX%\Scripts\activate >> "%PREFIX%\start_GSASII.bat"
echo python %PREFIX%\GSAS-II\GSASII\GSASII.py >> "%PREFIX%\start_GSASII.bat"
REM 
REM ============= Restore the git repository file
REM 
echo fix git files >> %logfile%
cd %PREFIX%\GSAS-II
REM echo rename keep_git .git >> %logfile%
REM      rename keep_git .git >> %logfile%
REM if errorlevel 1 exit 1
REM echo rename keep.gitignore .gitignore >> %logfile%
REM      rename keep.gitignore .gitignore >> %logfile%
REM if errorlevel 1 exit 1

echo C:\Windows\System32\tar.exe xzf git.tgz  >> %logfile%
     C:\Windows\System32\tar.exe xzf git.tgz  >> %logfile%

del git.tgz >> %logfile%
