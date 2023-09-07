# Starfield XGP Save Importer

An experimental tool to import .sfs savefiles into XGP savefile container.

## Usage

```
$ python3 main.py <path to .sfs file>
```

Or just drop the .sfs file onto the executable from releases.

**NOTE**: The cloud sync feature of Xbox app might interfere with outside modifications to the savefile container. After shutting down the game, please wait a minute or two before trying to import savefiles to give Xbox app some time to do the sync. 

## Path references

Steam version: `Documents\My Games\Starfield\Saves`

Xbox version: `%LOCALAPPDATA%\Packages\BethesdaSoftworks.Starfield_3275kfvn8vcwc\SystemAppData\wgs`