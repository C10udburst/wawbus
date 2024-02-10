=====
README
=====

Wawbus is a Python library for analyzing bus data from Warsaw Public Transport

Jupyter notebooks with analysis
-------------------------------

- `Part 1 <https://colab.research.google.com/github/C10udburst/wawbus/blob/master/part-one.ipynb>`_ (opens Google Colab)
- `Part 2 <https://colab.research.google.com/github/C10udburst/wawbus/blob/master/part-two.ipynb>`_ (opens Google Colab)

Part 1 covers analyzing bus speed and part 2 covers analyzing bus delays.

.. warning::
    When running notebooks via Google Colab, data collection is not possible.
    This is because api.um.warszawa.pl blocks requests from data center IPs.

Installation
------------

- Download whl file from `releases <https://github.com/C10udburst/wawbus/releases>`_
- Install it using pip:

.. code-block:: bash

    pip install wawbus-*-py3-none-any.whl


Usage in code
-------------

.. code-block:: python

    from wawbus import WawBus

    wb = WawBus(apikey='your_api')
    ## OR
    wb = WawBus(dataset='nameofdataset')

    wb.collect_positions(50)

    wb.dataset # pandas DataFrame with bus positions

    wb.calculate_speed() # retuns a new DataFrame with speed for each entry

Datasets are stored `here <https://github.com/C10udburst/wawbus-data>`_.

Usage in command line
---------------------

.. code-block::

    python3 -m wawbus --help

    usage: python3 -m wawbus [-h] [--apikey APIKEY] [--type {positions,timetable}] [--count COUNT] [--retry RETRY] [--sleep SLEEP] [--workers WORKERS] [--output OUTPUT]
    Collect bus positions from api.um.warszawa.pl

    options:
      -h, --help            show this help message and exit
      --apikey APIKEY       api.um.warszawa.pl API key. If set to 'env', will use WAWBUS_APIKEY.environment variable
      --type {positions,timetable,stops}
                            What to collect
      --count COUNT         number of collections
      --retry RETRY         number of retries
      --sleep SLEEP         sleep between collections
      --workers WORKERS     number of workers when collecting timetables
      --output OUTPUT       output file


