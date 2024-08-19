from typing import List, Final, Union, Literal, Optional
from pathlib import Path
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.theme import Theme
from wad3_reader import Wad3Reader

__version__ = '1.0.0'

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
    'fonts',
    'gfx',
    'spraypaint',
    'tempdecal',
]


app = typer.Typer()


def show_version(show: bool) -> None:
    if show:
        console.print(f"Which WAD v{__version__}", style='info', highlight=False)
        raise typer.Exit()

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

    return [glob for glob in globs if glob.stem.lower() not in WAD_SKIP_LIST]

def find_texture_in_wad(modpath: Path, texture: str) -> Union[Path, Literal[False]]:
    globs = find_wad_files(modpath)

    for glob in globs:
        if texture in Wad3Reader(glob):
            return glob
    
    return False


@app.command(no_args_is_help=True)
def main(
        mod_path: Annotated[Path, typer.Argument(
            help='path to the mod with the WAD files e.g. ".../steamapps/Half-Life/valve"',
            show_default=False)],
        texture: Annotated[str, typer.Argument(
            help='texture(s) to search for, use ";" to delimit multiple textures',
            show_default=False)],
        version: Annotated[Optional[bool], typer.Option(
            '--version', '-v', callback=show_version, is_eager=True,
            help='print application version', rich_help_panel=None)] = None,
        ) -> None:
    """Find which WAD in the mod path contains the specified texture"""

    if not mod_path.is_dir():
        console.print(f"{mod_path} is not a directory", style='error')
        raise typer.Exit(1)

    mod_path = unsteampipe(mod_path)
    textures = texture.split(';')

    for tex in textures:
        found_wad = find_texture_in_wad(mod_path, tex)
        tex = tex.upper()

        if not found_wad:
            console.print(
                f"Texture {tex} not found in any WAD in [not bold]{mod_path}[/not bold]",
                style='error')
            continue

        console.print(
            f"Texture [warning]{tex}[/warning] found in [success]{found_wad}[/success]")

if __name__ == '__main__':
    app()
