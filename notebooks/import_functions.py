from pyhdf.SD import SD, SDC 
import numpy as np
import pandas as pd
import re
import xml.etree.ElementTree as ET

def get_modis_filedata(path, datafield):
    hdf = SD(path, SDC.READ)  
    hdf_dict = hdf.datasets()
    # get keys in dictionary
    # for idx,sds in enumerate(hdf_dict.keys()):
    #     print (idx,sds)
    
    # get the object i want
    sds_obj = hdf.select('LST_Day_CMG') # select sds  
    data = sds_obj.get()               # get sds data

    data2D = hdf.select(datafield)
    data = data2D[:,:].astype(np.float64)
    return data, hdf


# props to https://stackoverflow.com/questions/48307678/how-i-create-lat-and-lon-in-my-modis-file-with-python3
def get_modis_meshgrid(hdf, data):
    # Read global attribute.
    fattrs = hdf.attributes(full=1)
    ga = fattrs["StructMetadata.0"]
    gridmeta = ga[0]
    
    # Construct the grid.  The needed information is in a global attribute
    # called 'StructMetadata.0'.  Use regular expressions to tease out the
    # extents of the grid. 
    ul_regex = re.compile(r'''UpperLeftPointMtrs=\(
                              (?P<upper_left_x>[+-]?\d+\.\d+)
                              ,
                              (?P<upper_left_y>[+-]?\d+\.\d+)
                              \)''', re.VERBOSE)
    match = ul_regex.search(gridmeta)
    x0 = np.float(match.group('upper_left_x')) 
    y0 = np.float(match.group('upper_left_y')) 

    lr_regex = re.compile(r'''LowerRightMtrs=\(
                              (?P<lower_right_x>[+-]?\d+\.\d+)
                              ,
                              (?P<lower_right_y>[+-]?\d+\.\d+)
                              \)''', re.VERBOSE)
    match = lr_regex.search(gridmeta)
    x1 = np.float(match.group('lower_right_x')) 
    y1 = np.float(match.group('lower_right_y')) 
    ny, nx = data.shape
    xinc = (x1 - x0) / nx
    yinc = (y1 - y0) / ny
    
    # make and return meshgrid
    x = np.linspace(x0, x0 + xinc*nx, nx)
    y = np.linspace(y0, y0 + yinc*ny, ny)
    xv, yv = np.meshgrid(x, y)
    # sinu = pyproj.Proj("+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")
    # wgs84 = pyproj.Proj("+init=EPSG:4326")
    # lon, lat= pyproj.transform(sinu, wgs84, xv, yv)
    return xv, yv


def readin_fis_biomass(filepath):
    
    try:
        tree = ET.parse(filepath)
    except:
        print(f'could not load file, {filepath}')
        return pd.DataFrame()
    
    root = tree.getroot()

    # get all reports from root
    reports = []
    report_attribs = []
    for x in root.iter('Row'):
        reports.append(x)
        report_attribs.append(x.attrib)


    # get all items from each report, save to dataframe
    attribs = pd.DataFrame()
    for r, r_a in zip(reports, report_attribs):
        try:
            r0 = r_a['r0']
        except:
            r0 = np.nan
        for a in r.iter('Column'):
            p = pd.DataFrame([a.attrib])
            p.loc[:,'r0'] = r0
            attribs = pd.concat([p, attribs])
    
    return attribs