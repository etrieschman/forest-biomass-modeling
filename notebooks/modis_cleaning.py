import pandas as pd
from shapely.geometry import Point, Polygon
import geopandas as gpd

from constants import GEO_CRS, PROJ_CRS

def clean_modis(df):
    # make variables
    df['date'] = pd.to_datetime(df.date_str.str[0:7], format='%Y%j')
    df['year'] = df.date.dt.year
    
    # set outlier as 5 times the 75th percentile
    PCTL, OUTL = 0.75, 3
    pctl_colname = 'pctl'+str(int(PCTL*100))
    df[pctl_colname] = df.prop.quantile(PCTL)
    print('Outlier threshold:', (OUTL * df[pctl_colname]).drop_duplicates().values)
    df['drop_outlier'] = df.prop >= OUTL * df[pctl_colname]
    print(f'Outliers dropped: {df.loc[df.drop_outlier].shape[0]} ({df.loc[df.drop_outlier].shape[0] / df.shape[0]:0.2%})')
    # drop outliers
    df = df.loc[~df.drop_outlier]
    
    return df


def add_consec_months_by_year(df, prop_col, mean_col, group_cols, year_col):
    ''' requires a dataframe of groupvars, yearcol, property column, 
    and mean of property across groupvars and yearcol '''
    # sort dataset
    df = df.sort_values(group_cols + [year_col])
    
    # merge on annual means
    annual_means = df.groupby(group_cols + [year_col])[prop_col].agg(['mean'])
    df = pd.merge(left=df, right=annual_means, how='left', on=('lat', 'lon', 'year'))
    
    # flag values lower than mean
    df['mbm'] = df[prop_col] < df[mean_col]
    # lag 1 and flag if first month below
    df['dbm'] = df['mbm'] & ~df.groupby(group_cols)['mbm'].shift(1).fillna(True)
    # get building blocks for max time below mean
    df['crossing'] = (df['mbm'] != df.groupby(group_cols + [year_col])['mbm'].shift(1).fillna(True)).cumsum()
    df['consec_mbm'] = df.groupby(group_cols + [year_col] + ['mbm', 'crossing']).cumcount(ascending=False) + 1

    # handle missing values created
    df.loc[~df.mbm, 'consec_mbm'] = 0
    
    return df


def aggregate_by_county(df, counties):
    # get county lat-lon mapping
    year = df.year.drop_duplicates().iloc[0]
    lat_lons = df.loc[df.year == year, ('lat', 'lon')]
    
    # make geodf
    geometry = [Point(xy) for xy in zip(lat_lons['lon'], lat_lons['lat'])]
    lat_lons = gpd.GeoDataFrame(lat_lons, crs=GEO_CRS, geometry=geometry)
    
    # spatial join with counties
    counties_sub = counties[['statefp', 'countyfp', 'name', 'geometry']]
    lat_lon_counties = gpd.sjoin(lat_lons, counties_sub, how='left', predicate='within')
    
    # subset
    lat_lon_counties = pd.DataFrame(lat_lon_counties.loc[lat_lon_counties.statefp.notna()])
    # merge onto full data
    df = pd.merge(left=df, right=lat_lon_counties, on=('lat', 'lon'), how='inner')
    
    # aggregate
    df = df.drop(['lat', 'lon', 'index_right', 'geometry'], axis=1)
    df = df.groupby(['year', 'statefp', 'countyfp', 'name']).agg(['mean', 'std'])
    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df = df.reset_index()
    
    return df