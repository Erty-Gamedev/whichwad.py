from typing import List, Final, Union, Literal
from pathlib import Path
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.theme import Theme
from wad3_reader import Wad3Reader

whichwad_theme = Theme({
    'success': 'bold green',
    'info': 'dim cyan',
    'warning': 'yellow',
    'error': 'bold red',
})
console = Console(theme=whichwad_theme)


STEAM_PIPES = ['_addon', '_hd', '_downloads']
WAD_SKIP_LIST: Final[List[str]] = [
    'cached',
    'decals',
    'fonts',
    'gfx',
    'spraypaint',
    'tempdecal',
]
SEARCH_ALL: Final[bool] = False


app = typer.Typer()


def unsteampipe(modpath: Path) -> Path:
    for pipe in STEAM_PIPES:
        if pipe in str(modpath):
            return modpath.parent / modpath.stem.replace(pipe, '')
    return modpath

def find_wad_files(modpath: Path) -> List[Path]:
    globs: List[Path] = []

    game = modpath.parent
    mod = modpath.stem

    for pipe in STEAM_PIPES:
        if (game / f"{mod}{pipe}").exists():
            globs.extend((game / f"{mod}{pipe}").glob('*.wad'))

    globs.extend(modpath.glob('*.wad'))

    if SEARCH_ALL:
        return globs
    
    return [glob for glob in globs if glob.stem.lower() not in WAD_SKIP_LIST]

def find_texture_in_wad(modpath: Path, texture: str) -> Union[Path, Literal[False]]:
    globs = find_wad_files(modpath)

    for glob in globs:
        if not SEARCH_ALL and glob.stem.lower() in WAD_SKIP_LIST:
            continue
        
        reader = Wad3Reader(glob)
        if texture in reader:
            return glob
    
    return False


def main(
        mod_path: Annotated[str, typer.Argument(
            help='path to the mod with the WAD files e.g. ".../steamapps/Half-Life/valve"',
            show_default=False)],
        texture: Annotated[str, typer.Argument(
            help='texture to search for', show_default=False)]
        ) -> None:

    modpath = unsteampipe(Path(mod_path))
    found_wad = find_texture_in_wad(modpath, texture)

    if not found_wad:
        console.print(
            f"Texture {texture} not found in any WAD in {modpath}",
            style='error')
        return

    console.print(
        f"Texture [warning]{texture}[/warning] found in [success]{found_wad}[/success]")

if __name__ == '__main__':
    typer.run(main)
