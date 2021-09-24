#!/usr/bin/env python3

from pathlib import Path
import subprocess
import re
from contextlib import contextmanager
import os
import argparse

import log2nc


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


class Case:
    def __init__(self, case_path):
        self.path = Path(case_path).resolve()

    def xmlquery(self, key):
        with cd(self.path):
            proc = subprocess.Popen(
                ['./xmlquery', key],
                stdout=subprocess.PIPE, encoding='utf-8'
            )
        return re.match(r'.*?=\s*(\S+)', proc.stdout.read()).group(1)

    def atm_logs(self):
        return Path(self.xmlquery('LOGDIR')).glob('atm.log.*')

    def convert(self, outdir):
        log2nc.convert(
            sorted(self.atm_logs()),
            outdir.joinpath(self.path.name+'.nc')
        )


def main():
    parser = argparse.ArgumentParser(
            description=(
                'read CESM atm logs and create Netcdf Files.'
            )
    )
    parser.add_argument(
            '--outdir', type=Path, nargs='?', default=Path.cwd(),
            help='directory for output NetCDF files'
    )
    parser.add_argument(
            'cases', nargs='*',
            help='text files containing the paths of cases.'
    )
    args = parser.parse_args()

    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    for item in args.cases:
        with open(item, 'r') as fin:
            for line in fin:
                Case(line.strip()).convert(outdir=args.outdir)


if __name__ == '__main__':
    main()
