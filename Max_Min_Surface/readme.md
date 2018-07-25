

# Dependencies
```python
#geospatial
from osgeo import gdal_array, gdal, osr
from affine import Affine
from rasterstats import zonal_stats
import rasterio

#operational
import os
import numpy as np
from glob import glob
import pandas as pd
```

Optionally for plotting:

```python
# Plotting
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pyproj
import matplotlib as mpl
```


# Process

The processing is designed to work within three main folders:

- input: contains input rasters and computational boundaries for metric calculation.  The desired directory structure is shown below:  

##Directory Structure

```bash
├───input
│   ├───0003L
│   │   └───DEMs_Unclipped
│   ├───0008L
│   │   └───DEMs_Unclipped
│   ├───0009L
│   │   └───DEMs_Unclipped
│   .
│   . <- Discontinuity in tree
│   
│   ├───
│   ├───0220R
│   │   └───DEMs_Unclipped
│   ├───0225R
│   │   └───DEMs_Unclipped
│   └───M006R
│       └───DEMs_Unclipped
├───output
└───scripts
```


- I have added the computational boundary shapefiles the site folder level of the directory.  I have uploaded the shapefiles in their desired location to the online reposotory.


- scripts: 
    - `start.py` - Main script to produce maximum and minimum surfaces
    - `sandbar_sd_coeff.py` - python file containing a dictornary of stage discharge coefficeints.  I used the mixed units stage discharge relationps (i.e. flow is in cfs and elevation is output in meters)

- output: This is where all of the output surfaces will be stored. 

THe process is centered around two functions within `start.py`. They are described below:

1. `get_surfaces`

    ```python
    Function to calulate max and min surface values for a set of rasters
    inputs:
        files = list of rasters to use in min and max suface calculations
        out_root = desired output root for output surface files
        site = string site code to use in output surface filexs 
        reatt (optional) = boolean, used to flag for reattachment bars at two bar sites
        sep (optional) = boolean, used to flag for separation bars at two bar sites
    File:      c:\workspace\sandbar_workbench_dev\scripts\<ipython-input-1-c82036f91a38>
    Type:      function
    ```
2. `eddy_metric_calculator`

    ```python
    Docstring:
    Function to calculate eddy metrics between max and min surfaces
    Inputs:
        max_surf: numpy ndarray containing max surface values
            Notes:
                nodata = -9999
        min_surf: masked array containg min surface values
        gt = geotransfrom for either the max of min surfaces
        shps = list containg path to eddy computational boundary shape file
            Notes:
                list is derived from glob.glob search
        site = string sitecode parsed from input rasters
        raster_out (optional) = flag to output intermediate processing rasters for manual caluations
        reatt (optional)= boolean, true if processing the reattchement bar at a two bar site.
        sep (optional)= boolean, true if processing the separation bar at a two bar site.
    File:      c:\workspace\sandbar_workbench_dev\scripts\<ipython-input-1-c82036f91a38>
    Type:      function
    ```

The resulting max surface metrics are output as the dictionary `result`. The results can also be reviewed the pandas dataframe `df`, see below:

#### Eddy_Metrics
|SiteCode |Max_Area_Eddy_Low|Max_Area_Eddy_HE|Max_Vol_Eddy_HE|Max_Vol_Eddy_Low|Max_Area_Eddy_FZ|Max_Vol_Eddy_FZ|
|---------|----------------:|---------------:|---------------|---------------:|---------------:|--------------:|
|0003L    |           3037.2|           433.8|         312.98|       13390.319|          4132.0|         3961.7|
|0009L    |           7719.2|          1548.6|        1217.88|         476.316|          2997.9|         3816.5|
|0016L    |           6112.6|           471.0|         171.53|       22604.207|          1570.0|         1427.8|
|0022R    |           4048.9|          1066.8|        1688.58|       12049.206|          2174.6|         2972.1|
|0030R    |           3844.2|          2354.3|        3160.76|       10453.497|          2422.0|         3324.7|
|0032R    |           6471.2|          1275.8|        1256.11|       26427.968|          3872.5|         3100.2|
|0043L    |           2975.9|          3118.1|        3795.96|        8017.490|          2365.0|         3329.1|
|0047R    |          17815.2|          2812.0|        2677.66|       73587.509|          7858.9|         7181.9|
|0051L    |          16534.5|          8197.3|        8356.10|       70025.575|          6955.2|         6478.6|
|0055R    |           9593.1|          8442.9|        6127.66|       44084.608|          6946.4|         5917.9|
|0062R    |           8104.6|          4262.0|        1477.76|       63811.935|          3579.4|         3508.9|
|0068R    |           7545.2|          4143.7|        3437.19|       22033.924|          3430.7|         2629.8|
|0070R    |            682.6|          1770.9|        1897.09|          94.048|          1666.0|         1072.8|
|0081L    |           1031.7|          1904.6|        2686.11|         774.103|           498.1|          536.3|
|0087L    |            173.8|           393.4|         459.55|         362.745|           585.9|          595.2|
|0091R    |           2491.1|           607.5|        1433.02|        9100.439|          1281.9|         1319.6|
|0093L    |            957.6|          1485.2|        1237.64|        2677.386|          1149.4|         1109.9|
|0104R    |            368.8|           336.2|         396.54|         677.349|           316.4|          394.4|
|0119R    |           4447.7|          2635.8|        3925.36|       12359.915|          1846.2|         2088.4|
|0122R    |           1842.5|          2802.6|        3095.75|        5423.590|          3596.2|         4424.2|
|0123L    |           5102.6|          1352.2|        2521.23|       13911.327|          2068.5|         2522.6|
|0137L    |           1276.7|          1655.1|        2234.90|        1558.111|          2205.2|         3645.0|
|0139R    |           4951.6|           814.5|         748.39|       11999.887|          1418.2|         1960.1|
|0145L    |            185.0|           678.4|        1206.21|         277.996|           412.1|          634.7|
|0172L    |           3327.4|          3594.6|        3630.47|        7988.186|          2536.7|         3166.5|
|0183R    |           1853.9|          1519.1|        3205.38|        4269.561|          1708.6|         2410.7|
|0194L    |           4175.1|          6768.9|        8147.85|       12548.649|          3196.3|         4085.6|
|0213L    |           1382.9|          1404.4|        2234.34|        4609.920|          1205.6|         2693.7|
|0220R    |            427.1|          1665.6|        2082.69|         762.185|           355.2|          275.5|
|0225R    |           2163.1|          2118.1|        2075.15|        9413.267|          1354.5|         1296.3|
|M006R    |           5802.0|           788.5|         645.38|       10422.316|          4514.9|         3850.0|
|0008L    |            363.9|          1300.1|         975.87|         867.982|          1278.3|         1091.8|
|0024L    |            159.2|           289.0|          60.44|          45.859|          2291.6|         4124.2|
|0029L    |            410.3|          1188.0|         982.53|          78.693|          1381.9|         1627.1|
|0033L    |            149.4|          3449.7|       10518.76|          49.484|          1233.6|         1279.6|
|0056R    |            147.2|          2889.4|        2067.03|           5.854|          1977.2|         1326.3|
|0084R    |             95.5|           340.9|         491.89|           7.882|           746.6|          907.3|
|0167L    |             18.0|          2987.7|        3873.90|           2.927|          2060.7|         2578.7|
|0035L_r_r|          14483.3|             0.0|--             |       49799.660|          2176.7|         2615.8|
|0041R_r_r|          13039.6|          5366.2|        4545.73|       14084.200|         10862.7|         8978.2|
|0044L_r_r|           9458.6|          2791.7|        3101.62|       39291.744|          6015.9|         6440.7|
|0045L_r_r|          10178.0|          2814.6|        3335.53|       20367.690|          3648.7|         4168.4|
|0050R_r_r|           1665.5|          1769.1|        3477.50|        3354.543|          1492.9|         1610.5|
|0063L_r_r|          14039.2|          3654.7|        4959.82|       80445.865|          4865.4|         5989.4|
|0065R_r_r|           4233.2|          2813.4|        2331.90|       18604.384|          5937.2|         4462.2|
|0202R_r_r|           7324.8|             0.0|--             |       32726.652|           892.9|          552.2|
|0035L_s_r|           1770.0|           918.2|        1247.92|        2566.100|          1710.8|         2280.2|
|0041R_s_r|           4049.0|          3077.6|        4135.97|        3021.229|          3932.2|         4557.7|
|0044L_s_r|           2691.6|          2394.0|        3590.30|        5533.116|          2075.9|         2751.5|
|0045L_s_r|           3402.4|           883.1|        1061.73|        6433.212|          1613.6|         2007.0|
|0050R_s_r|           2045.3|          1259.3|        1799.79|        2048.340|           914.1|          947.6|
|0063L_s_r|           3044.7|           639.5|         493.98|        8634.239|          1608.2|         1856.6|
|0065R_s_r|            378.9|           904.2|         590.06|        1065.012|          1951.3|         1994.5|
|0202R_s_r|           2616.3|          1648.9|        1816.44|        8385.728|   1453.4|         1689.6|