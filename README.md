# CHS-DVD-Reader
pip install pyqt5
pip install pyqt5-tools

## to open pyqt5 designer:
in anaconda command prompt type "designer"
or find the .exe and create a shortcut (C:\Users\wayne\anaconda3\Library\bin\designer.exe)

## Qt Designer
once initial design saved, go to the directory and execute to build .py code:
pyuic5 filename.ui -o newfilename.py
create a shortcut for designer.exe; >***\anaconda3\envs\chs\Lib\site-packages\qt5_applications\Qt\bin

## Useful terminal window commands to view SQLite database:
>sqlite3 chs_dvd.db<br>
sqlite>.help<br>
sqlite>.tables<br>
sqlite>.schema table_name<br>
sqlite>SELECT * FROM table_name LIMIT n;<br>

## install sqlite browser
google sqlitebrowser and download / install DB Browser for SQLite - Standard installer for 64-bit windows


## TODO (dated 27 Oct 23)
add master_database entry to misc_reports so user can compare and see the difference.
once done and happy user selects "accept current month as new master database"; delete chs_dvd.db and rename current_month.db to chs_dvd.db
create .pdf report; format to mimic NOTMAR .pdf format; use ReportLab open-source library
convert to app.

