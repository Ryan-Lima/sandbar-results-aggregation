# Survey Stage Analysis
THis repostirory was to created to store all of the materials required to calculate the stage at individual surveys.  All survey shouts surveyed with a water surface attribute are queried from the points file, clipped to the computational boundary extent, and exported to their own file.

Clone this repository to:
```
C:\workspace\
```
#Install
These scripts need the following packages to run:
```
Pandas
OGR

```
Pandas is included in the anaconda distribution of python.  I used a Windows 10 environment to develop all of the included scrits with [Anaconda disbribution](https://www.continuum.io/downloads#_windows). 
```
https://www.continuum.io/downloads#_windows
```

Installing GDAL/OGR on a windows machine involves downloading (1) downloading the binaries and (2) installing osego for python. 
The binaries are hosted at:
```
http://www.gisinternals.com/release.php
```
##Note: Must install binaries before you install the python bindings
Take care an make sure you choose your python distibution and compiler to get the correct download.  My machine used the MSC v.1500 64 bit (AMD64) compiler with 64 bit python 2.7.  To tell anaconda where the GDAL bianaries are located, Download the whl file:
```
http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
```
and install using 
```
pip install GDAL-2.0.3-cp27-cp27m-win_amd64.whl
```
The computational boundaries were provided in an ESRI File Geodatabase format.  I wanted to develop an open-source workflow so I extracted the all of the feature classes using the `ogr2ogr` tool to export individual shapefiles.  `ogr2ogr` is included with any QGiS application.  The executable file can be found in the bin directory of the program:
```
C:\Program Files\QGIS Wien\bin\ogr2ogr.exe
```
If you dont have qgis, I have found an `ogr2ogr` [GUI](http://ogr2gui.ca/) at:
```
http://ogr2gui.ca/
```
#Procedure
To extract shapefiles using the `ogr2ogr` is a command line tool:
```
ogr2ogr -f "ESRI Shapefile" C:\workspace\survey_stage\shp C:\workspace\survey_stage\NAU_comp_bnds.gdb 
```

To build the shapefile lookup table `LU_site_shape_path.csv` run `scripts/shp_lu_builder.py`
This script is a bit clunky, but it works.  The site list is read in using the `survey_stage_2015_06_25.xlsx` workbook.  This path could be chagned if a newer export is avaialble.  

To subset the points files in `NAU_Survey_PTS_Files/` run `scripts/subset_pts_files.py`
This script subsets the points files and writes individual points files to `WSE_Points/`.  These files will work with the `Survey_Stage.xlsm` workbook.  
Not knowing if these water surface points will be used in any other analyses, I exported all of water surface elevation points `Merged_WSE_PTS/` directory.  I appended the date found on the original pts file. 



