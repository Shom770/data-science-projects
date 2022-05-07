import bisect
import math
import operator
import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.font_manager as font_manager
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from matplotlib.offsetbox import AnchoredText

from historical_hrrr_temps import historical_hrrr_temps


print(historical_hrrr_temps(data_time=datetime.datetime(2021, 2, 18)))