=====
wawbus
=====

Wawbus is a Python library for analyzing bus data from Warsaw Public Transport

Installation
------------

- Download whl file from `releases <https://github.com/C10udburst/wawbus/releases>`_
- Install it using pip:

.. code-block:: bash

    pip install wawbus-*-py3-none-any.whl

Usage
-----

.. code-block:: python

    from wawbus import WawBus

    wb = WawBus(apikey='your_api')
    ## OR
    wb = WawBus(dataset='nameofdataset')

    wb.collect_positions(50)

    wb.dataset # pandas DataFrame with bus positions

    wb.calculate_speed() # retuns a new DataFrame with speed for each entry

Datasets are stored `here <https://github.com/C10udburst/wawbus-data>`_.