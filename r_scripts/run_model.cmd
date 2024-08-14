@echo off
setlocal
set "batchDir=%~dp0"
@REM echo The directory of this batch file is: %batchDir%
endlocal

cd batchDir

set FILE_PATH=%USERPROFILE%\AppData\Local\Programs\R\R-4.3.3\bin\Rscript.exe

if exist "%FILE_PATH%" (
    echo Running Programs
    %FILE_PATH% run_according_to_config.R
) else (
    echo "I Could Not Find a valid R environment installed on this PC"
    echo "Please Check the following:"
    echo "   1) Is R installed? This version is known to work: https://cran.r-project.org/bin/windows/base/old/4.3.3/R-4.3.3-win.exe <- try this version before any others"
    echo "   2) Is the correct version of R installed? You can try the currently installed version (change line 9 on this file), else Please install version 4.3.3 as this has been validated to work"
    echo "   3) Where is R installed? If R is installed in a different place, open this script and change the file path accordingly."
)
pause