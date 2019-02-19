# Introduction
pyTypo 0.1 is a prank typo program written in Python.  It only works under Windows, where it will run silently in the background upon startup.  The program randomly creates four different kinds of mistakes:
  * Reversed letters  (e.g. "Please join me for lnuch")        50%
  * Wrong letters (nearby) (e.g. "Please join me for lumch")   20%
  * Missing letters  (e.g. "Please join me for luch")          15%
  * Extra letters (nearby)  (e.g. "Please join me for lunmch") 15%
 
Settings within the Python script control when the typos are triggered, with the default settings as follows:
```python
time_threshold = 125  # trigger based on fast typing (delays of less than 125ms between characters)
random_percentage = 30  # Don't typo _every_ time we trigger, only about 30% of the time.
resume_timeout = 17000  # After a typo, wait 17 seconds before allowing another one.
```

# Requirements
## [Python 3.6 for Windows](https://www.python.org/ftp/python/3.6.7/python-3.6.7.exe)
Although Python 3.6.7 is referenced by the installation script, you can modify the version as needed.  Typically, a silent installation can be triggered as follows:
`python-3.6.7.exe /quiet InstallAllUsers=1 Shortcuts=0 Include_tcltk=0 PrependPath=1`
This will install into `%ProgramFiles(x86)%\Python36-32`

## [pyHook 1.5.1](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook)
The .whl file is included, and can be installed with this command:
`pip install pyHook-1.5.1-cp36-cp36m-win32.whl`

## pythoncom (part of pywin32)
The .whl file is included, and can be installed with either of these commands:
`pip install pywin32`    (gets it from the main repo)
`pip install pywin32-224-cp36-cp36m-win32.whl`   (uses the included file)


# Installation
Download Python 3.6 (32 bit) from the link above, then copy the contents of the install folder and the tpo.py script to a USB stick.  As a user with administrative privileges, run `install.bat` to install, or `upgrade.bat` to update the script.  The tpo.py script is placed into the `%ProgramFiles(x86)%\Python36-32` folder, and is run silently by the current user on startup.  Feel free to adjust the installation script as desired!


# Additional ideas for further development
  * Pay attention to the backspace and delete buttons.  As they are used more often, scale back the frequency of typos.
  * Get worse with more typing, or get worse throughout the day.
  * Auto-adjust to the speed of the current typing, using standard deviation to decide where to place the trigger.


# More information
Average typing speed is between 38-40 WPM  (or 190 - 200 characters per minute).  This translates to an average of 300ms between characters, but the maximum speed varies greatly.  Average normal accuracy is 8 typos for every 100 words typed, or about 3.2 typos per minute on average.

