from typing import Final, Optional
from pathlib import Path
import fnmatch
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.theme import Theme
from wad3_reader import Wad3Reader

__version__ = '1.1.0'

STEAM_PIPES = ['_addon', '_hd', '_downloads']
WAD_SKIP_LIST: Final[list[str]] = [
    'cached',
    'fonts',
    'gfx',
    'spraypaint',
    'tempdecal',
]

whichwad_theme = Theme({
    'success': 'bold green',
    'info': 'dim cyan',
    'warning': 'yellow',
    'error': 'bold red',
    'wad': 'grey42',
})
console = Console(theme=whichwad_theme, tab_size=2)


app = typer.Typer(add_completion=False)


def show_version(show: bool) -> None:
    if show:
        console.print(f"Which WAD v{__version__}", style='info', highlight=False)
        raise typer.Exit()

def unsteampipe(modpath: Path) -> Path:
    for pipe in STEAM_PIPES:
        if pipe in str(modpath):
            return modpath.parent / modpath.stem.replace(pipe, '')
    return modpath

def find_wad_files(modpath: Path) -> list[Path]:
    globs: list[Path] = []

    game = modpath.parent
    mod = modpath.stem

    for pipe in STEAM_PIPES:
        if (game / f"{mod}{pipe}").exists():
            globs.extend((game / f"{mod}{pipe}").glob('*.wad'))

    globs.extend(modpath.glob('*.wad'))

    return [glob for glob in globs if glob.stem.lower() not in WAD_SKIP_LIST]

def find_texture_in_wad(
        globs: list[Path],
        texture: str,
        readers: dict[Path, Wad3Reader]) -> dict[str, list[Wad3Reader]]:
    found_wads: dict[str, list[Wad3Reader]] = {}
    
    for glob in globs:
        if glob not in readers:
            readers[glob] = Wad3Reader(glob)
        reader = readers[glob]

        matches = fnmatch.filter(reader.textures.keys(), texture)
        for match in matches:
            if match not in found_wads:
                found_wads[match] = []
            found_wads[match].append(reader)

    return found_wads


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
        extract: Annotated[bool, typer.Option(
            '--extract', '-e', help='extract the textures')] = False,
        output: Annotated[Path, typer.Option(
            '--output', '-o', help='output directory for extracted textures',
            show_default=True, dir_okay=True, writable=True, file_okay=False)] = Path('extracted')
        ) -> None:
    """Find which WAD in the mod path contains the specified texture"""

    if not mod_path.is_dir():
        console.print(f"{mod_path} is not a directory", style='error')
        raise typer.Exit(1)
    
    mod_path = unsteampipe(mod_path)
    globs = find_wad_files(mod_path)
    textures = texture.split(';')
    all_found_wads: dict[str, dict[str, list[Wad3Reader]]] = {}
    readers: dict[Path, Wad3Reader] = {}

    for tex in textures:
        found_wads = find_texture_in_wad(globs, tex, readers)

        if not found_wads:
            console.print(
                f"No texture names matching [cyan]'{tex}'[/cyan] not found in any WAD "\
                f"in [not bold]{mod_path}[/not bold]", style='error', highlight=False)
            continue
        
        all_found_wads[tex] = found_wads

        console.print(
            f"[success]{len(found_wads)}[/success] texture names matching "\
                f"[magenta]'{tex}'[/magenta] found:",
            style='info', highlight=False)

        for match, wads in found_wads.items():
            console.print(
                f"\t[warning]{match.upper()}[/warning] found in {len(wads)} WADs:",
                style='info')
            for wad in wads:
                console.print(f"\t{wad.file}", style='wad')

    if not extract or not len(all_found_wads):
        return
    
    console.print('')
    
    if not output.exists():
        confirm_create_dir = typer.confirm(
            f"{output.absolute()} does not exist. Create it?")
        if not confirm_create_dir:
            console.print('Output dir not created, aborted', style='error')
            raise typer.Exit(2)
        output.mkdir()
        console.print(f"{output.absolute()} created", style='info')

    for tex, found_wads in all_found_wads.items():
        for match, wads in found_wads.items():
            output_file = output / f"{match.upper()}.bmp"

            if len(wads) == 1:
                console.print(
                    f"Saving texture from {wads[0].file.name} "\
                    f"to [bold]{output_file}[/bold]", style='info')
                wads[0][match.lower()].save(output_file)
                continue

            console.print(
                f"[warning]{match.upper()}[/warning] found in {len(wads)} WADs. It's time to choose:",
                style='green', highlight=False)
            
            for wad in wads:
                confirm_savetex = typer.confirm(f"Extract from {wad.file.name}?")
                if confirm_savetex:
                    console.print(
                        f"Saving texture from {wad.file.name} "\
                        f"to [bold]{output_file}[/bold]", style='info')
                    wad[match.lower()].save(output_file)
                    break

if __name__ == '__main__':
    app()
