from typing import Final, Literal
from pathlib import Path
from itertools import batched

ENDIANESS: Final[Literal['little']] = 'little'

class BmpImage:
    def __init__(self, dimensions: tuple[int, int], data: bytes, palette: bytes) -> None:
        self.dimensions = dimensions
        self.data = data
        self.palette = palette

    def convert_pixel_data(self) -> bytes:
        """WAD pixel data is stored top-down, left-to-right,
        while BMP pixel is stored bottom-up, left-to-right."""

        rows: list[tuple[int, ...]] = list(batched(list(self.data), self.dimensions[1]))
        rows = list(reversed(rows))
        data = b''

        for row in rows:
            data += b''.join(
                [i.to_bytes(1, byteorder=ENDIANESS) for i in row]
            )

        return data


    def convert_palette(self) -> bytes:
        """BMP palettes uses 4 bytes per colour.
        Blue, Green, Red, one byte each, and an unused 4th byte
        """

        colours = batched(list(self.palette), 3)

        # BMP palettes uses 4 bytes per colour
        # Blue, Green, Red, one byte each, and an unused 4th byte
        bmp_palette = b''

        for red, green, blue in colours:
            bmp_palette += blue.to_bytes(1, byteorder=ENDIANESS)
            bmp_palette += green.to_bytes(1, byteorder=ENDIANESS)
            bmp_palette += red.to_bytes(1, byteorder=ENDIANESS)
            bmp_palette += b'\x00'
        
        return bmp_palette

    def save(self, filename: Path) -> None:
        width, height = self.dimensions
        size = width * height
        with filename.open('wb') as file:
            # Begin Header

            file.write(b'\x42\x4D') # Signature
            size_header = 1078 # Header (14) + InfoHeader (40) + Palette (4*256)
            filesize = size_header + size # size_header + image pixels
            file.write(filesize.to_bytes(4, byteorder=ENDIANESS))
            file.write(bytes(4)) # Reserved
            file.write(size_header.to_bytes(4, byteorder=ENDIANESS)) # Offset to image data

            # Begin InfoHeader
            file.write((40).to_bytes(4, byteorder=ENDIANESS)) # InfoHeader size
            file.write(width.to_bytes(4, byteorder=ENDIANESS)) # Image Width
            file.write(height.to_bytes(4, byteorder=ENDIANESS)) # Image Height
            file.write(b'\x01\x00') # Planes (1)
            file.write(b'\x08\x00') # Bits per pixel (8)
            file.write(bytes(4)) # Compression (0, none)
            file.write(size.to_bytes(4, byteorder=ENDIANESS)) # Image size (width*height)
            file.write((3780).to_bytes(4, byteorder=ENDIANESS)) # Horizontal pixels per meter
            file.write((3780).to_bytes(4, byteorder=ENDIANESS)) # Vertical pixels per meter
            file.write((256).to_bytes(4, byteorder=ENDIANESS)) # Number of colours used
            file.write((256).to_bytes(4, byteorder=ENDIANESS)) # Important colours
            
            # Begin Colour Palette
            file.write(self.convert_palette())

            # Begin Pixel Data
            file.write(self.convert_pixel_data())
