# evolving-CO2-in-ExoCAM

Here are Fortran source files used in the paper, "Evolving CO2 rather than
SST leads to a factor of ten decrease in GCM convergence time". These source
files should be used with [ExoCAM](https://github.com/storyofthewolf/ExoCAM).

## Requirements

You need to know how to run ExoCAM aqua-planet simulations \(E2000C4AQN or
E2000C4AQI\) with sea ice turned off.


## Usage

First, create an ExoCAM aqua-planet case \(E2000C4AQN or E2000C4AQI,
referred to as `"${EXOCAM_CASE}"`\).

Second, turn off sea ice by decreasing the freezing point of sea water
\(`SHR_CONST_TKFRZSW` in `SourceMods/src.share/shr_const_mod.F90`\).

Third, copy `SourceMods` to the case. In this process, some files are
overwritten.
```bash
$ cp -Ryv SourceMods "${EXOCAM_CASE}"
```

Fourth, change parameters. The global-mean SST is `sst_expct` in
`SourceMods/src.docn/docn_comp_mod.F90`. The CO2 e-folding timescale
is `efld_time` in `SourceMods/src.cam/prog_mod.F90`.

Finally, build and run the simulation.

The evolution of CO2 only shows in the log file of the atmosphere model. We
use `get_co2.py`  to collect the CO2 data in the log file and create an NetCDF
file for each simulation.

## License
[MIT](https://choosealicense.com/licenses/mit/)
