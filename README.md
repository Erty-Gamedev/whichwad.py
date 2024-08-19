# Which WAD

A simple CLI utility tool for finding out which WAD of a mod that contains a specific texture.

SteamPipe directories such as `_addon` and `_downloads` are automatically searched within.

## Usage

### Basic usage

To find which WAD in CS 1.6 that *some_texture* exists in:

```cli
python whichwad.py C:/Steam/steamapps/Half-Life/cstrike some_texture
```

### Search for multiple textures

Multiple textures can be searched for at the same time by delimiting the
texture names with a semicolon, e.g.: `my_texture1;+0_other_texture;!water_texture`

### Extract textures

Textures can also be extracted from the found WAD files using the `--extract` argument.
The `--output` argument can be used to specify where to extract the textures to.

```cli
python whichwad.py C:/Steam/steamapps/Half-Life/cstrike generic1;generic3 --extract --output C:/projects/cs_banana/extracted
```

By default extracted textures will be placed in a subfolder of the script named *extracted*.
