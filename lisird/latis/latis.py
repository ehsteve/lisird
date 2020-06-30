from io import StringIO
import requests
import urllib
import tempfile
import pandas as pd

from astropy.time import Time

import lisird

LATIS_DATA_URL = 'https://lasp.colorado.edu/lisird/latis/dap'
LATIS_DATE_FORMAT_CMD = "format_time(yyyy-MM-dd'T'HH:mm:ss.SSS)"

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

__all__ = [
    "get_file_with_times",
    "get_data_with_times",
    "url_with_times",
    "get_last_data",
    "load_dataset_file"
]


def get_file_with_times(dataset, start_time, end_time):
    """
    Searches for and downloads a file with data from a dataset for a specified
    time range. For all supported datasets see :download:`datasets.csv <../../lisird/data/datasets.csv>`.
    The file must be moved to a permanent location for long-term storage.

    Parameters
    ----------
    dataset : str
        The name of the dataset.
    start_time : `astropy.time.Time`
        The start of the region of interest.
    end_time : `astropy.time.Time`
        The end of the region of the interest.

    Return
    ------
    file_string : str
        The temporary filename.

    Examples
    --------
    >>> from lisird.latis import get_file_with_times
    >>> from astropy.time import Time
    >>> f = get_file_with_times('sorce_tsi_24hr_l3', Time('2005-05-05T12:00', Time('2006-05-05T12:00')
    """
    url = url_with_times(dataset, start_time, end_time)
    download_filename = _download_to_tempfile(url)
    return download_filename


def get_data_with_times(dataset, start_time, end_time):
    """Retrieve data from a dataset for a specific time range.

    Parameters
    ----------
    dataset : str
        The name of the dataset.
    start_time : `astropy.time.Time`
        The start of the region of interest.
    end_time : `astropy.time.Time`
        The end of the region of the interest.

    Return
    ------
    data : `pandas.DataFrame`

    Examples
    --------
    >>> from lisird.latis import get_data_with_times
    >>> from astropy.time import Time
    >>> f = get_data_with_times('sorce_tsi_24hr_l3', Time('2005-05-05T12:00', Time('2006-05-05T12:00')
    """
    url = url_with_times(dataset, start_time, end_time)
    r = requests.get(url, stream=True)
    data = pd.read_csv(StringIO(r.content.decode("ASCII")), index_col=0,
                       parse_dates=True)
    return data


def get_last_data(dataset):
    """Retrieve the latest datum from a dataset.

    Parameters
    ----------
    dataset : str
        The name of the dataset.

    Return
    ------
    data : `dict

    Examples
    --------
    >>> from lisird.latis import get_last_data
    >>> data = get_last_data('sorce_tsi_24hr_l3')
    """
    url = f"{LATIS_DATA_URL}/{dataset}.csv?last()&{LATIS_DATE_FORMAT_CMD}"
    r = requests.get(url, stream=True)
    result = StringIO(r.content.decode("ASCII")).getvalue()
    result = {result.split('\n')[0].split(',')[0]: result.split('\n')[1].split(',')[0],
              result.split('\n')[0].split(',')[1]: result.split('\n')[1].split(',')[1]}
    return result


def load_dataset_file(filepath):
    """Parse a dataset file and load the data.

    Parameters
    ----------
    filepath : str
        The path to the dataset.

    Return
    ------
    data : `pandas.DataFrame`

    Examples
    --------
    >>> from lisird.latis import get_file_with_times, load_dataset_file
    >>> from astropy.time import Time
    >>> filepath = get_data_with_times('sorce_tsi_24hr_l3', Time('2005-05-05T12:00', Time('2006-05-05T12:00')
    >>> data = load_dataset_file(filepath)

    """
    data = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return data


def _download_to_tempfile(url):
    """A utility function to retrieve a url to a semi-permamanet temporary file"""
    download_file = tempfile.NamedTemporaryFile(delete=False)
    result = urllib.request.urlretrieve(url, download_file.name)
    return download_file.name


def url_with_times(dataset, start_time, end_time):
    """Construct a url to retrieve data from a specificied dataset within
    a time range.

    ..note : This functions performs a number of checks to ensure that invalid
    urls cannot be constructed.

    Parameters
    ----------
    dataset : str
        The name of the dataset.
    start_time : `astropy.time.Time`
        The start of the region of interest.
    end_time : `astropy.time.Time`
        The end of the region of the interest.

    Return
    ------
    url : str

    """
    if end_time <= start_time:
        raise ValueError(f"Start time {start_time} must be less than end time {end_time}.")

    if dataset not in lisird.dataset_list:
        raise ValueError(f"Dataset {dataset} is not recognized. Consider updating your catalog if this message is not expected.")

    url = f"{LATIS_DATA_URL}/{dataset}.csv?{LATIS_DATE_FORMAT_CMD}&"
    url += f'time>={start_time.strftime(_TIME_FORMAT)}&time<{end_time.strftime(_TIME_FORMAT)}'
    return url
