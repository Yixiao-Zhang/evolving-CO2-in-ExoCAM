import re
import gzip

import numpy as np
from netCDF4 import Dataset


def convert(logs, ncout):

    values = list()
    flnt = list()
    fsnt = list()

    def read_lbl(fname):
        if fname.name.endswith('.gz'):
            return gzip.open(fname, 'rt')
        else:
            return open(fname, 'r')

    for log in logs:
        for line in read_lbl(log):
            match = re.match(r'\s*CO2\s*MMR\s*:\s+(\d+\.\d+)\s+ppmr\s*', line)
            if match:
                values.append(float(match.group(1)))
            match = re.match(r'\s*FLNT\s*\(W/m2\)\s+(\d+\.\d+)\s*', line)
            if match:
                flnt.append(float(match.group(1)))
            match = re.match(r'\s*FSNT\s*\(W/m2\)\s+(\d+\.\d+)\s*', line)
            if match:
                fsnt.append(float(match.group(1)))

    time_day = (np.arange(len(values)) + 0.5)/48

    values, fsnt, flnt = map(np.array, (values, fsnt, flnt))

    dset = Dataset(ncout, 'w', format='NETCDF4')

    dset.createDimension('time', None)

    datatype = 'float64'
    dims = ('time', )

    def my_create_variable(*args, **kwargs):
        kwargs['fletcher32'] = True
        kwargs['zlib'] = True
        kwargs['shuffle'] = True
        kwargs['complevel'] = 4
        return dset.createVariable(*args, **kwargs)

    v_name = 'time'
    variable = my_create_variable(v_name, datatype, dims)
    variable.setncatts(dict(
        long_name='time',
        units='days since 0001-01-01 00:00:00',
        calendar='noleap',
        bounds='time_bnds'
    ))
    variable[:] = time_day

    v_name = 'co2mmr'
    variable = my_create_variable(v_name, datatype, dims)
    variable.setncatts(dict(
        long_name='co2mmr',
        units='ppm',
        cell_methods='time: mean'
    ))
    variable[:] = values

    v_name = 'FLNT'
    variable = my_create_variable(v_name, datatype, dims)
    variable.setncatts(dict(
        long_name='Net longwave flux at top of model',
        units='W/m2',
        cell_methods='time: mean'
    ))
    variable[:] = flnt

    v_name = 'FSNT'
    variable = my_create_variable(v_name, datatype, dims)
    variable.setncatts(dict(
        long_name='Net shortwave flux at top of model',
        units='W/m2',
        cell_methods='time: mean'
    ))
    variable[:] = fsnt

    dset.close()
