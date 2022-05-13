from pathlib import Path
import matplotlib as matplotlib
import matplotlib.pyplot as plt

# Paths
REPO_PATH = Path('/Users/etriesch/dev/forest-biomass-modeling/')
DATA_PATH = REPO_PATH / 'data/'
DATA_CLEAN_PATH = DATA_PATH / 'data/clean/'
GEO_CRS = 'epsg:4326'
PROJ_CRS = '+proj=cea'


# chart settings
def set_plt_settings():
    plt.rcParams.update({'font.size': 18})
    SMALL_SIZE = 10
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 20

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
