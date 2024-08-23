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

### Pattern matching / wildcard search

The *fnmatch* library is used to allow for UNIX filename pattern matching.

| Pattern  | Match                              |
| -------- | ---------------------------------- |
| `*`      | matches everything                 |
| `?`      | matches any single character       |
| `[seq]`  | matches any character in *seq*     |
| `[!seq]` | matches any character not in *seq* |

*(From https://docs.python.org/3/library/fnmatch.html)*

This way you can match any texture name beginning with *generic*
by searching for "generic*".

### Extract textures

Textures can also be extracted from the found WAD files using the `--extract` argument.
The `--output` argument can be used to specify where to extract the textures to.

```cli
python whichwad.py C:/Steam/steamapps/Half-Life/cstrike generic1;generic3 --extract --output C:/projects/cs_banana/extracted
```

By default extracted textures will be placed in a subfolder of the script named *extracted*.
