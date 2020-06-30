# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
from pathlib import Path
import urllib.request
import json

from astropy.table import Table

try:
    from .version import __version__
except ImportError:
    __version__ = "unknown"
__all__ = []

_package_directory = os.path.dirname(os.path.abspath(__file__))
_data_directory = os.path.abspath(os.path.join(_package_directory, 'data'))


def download_catalog_file():
    catalog_url = 'https://lasp.colorado.edu/space-weather-portal/latis/catalog'
    result = urllib.request.urlretrieve(catalog_url, catalog_file)


def read_catalog(url):
    with open(url) as f:
        data = json.load(f)
    col_names = list(data['dataset'][0].keys())
    data_dict = {}
    for this_col in col_names:
        these_data = [this_data.get(this_col, '') for this_data in data['dataset']]
        data_dict.update({this_col.replace('@', ''): these_data})
        if this_col.count('distribution') > 0:
            names = [this_data[0]['accessURL'].split('/')[-1] for this_data in these_data]
            data_dict.update({'names': names})
    # data_dict = {'name': [this_value[0].get('accessURL', '') for this_value in data_dict['distribution']]}
    result = Table(data_dict)
    result.add_index('names')
    return names, data, data_dict

catalog_file = Path(os.path.join(_data_directory, 'catalog.txt'))

#if not catalog_file.is_file():
#    download_catalog_file()

#dataset_list, catalog_data, data_dict = read_catalog(catalog_file)

with open(os.path.join(_data_directory, 'datasets.csv')) as f:
    dataset_list = [line.strip() for line in f]