# Recibirá archivos de imagen como parámetros y será capaz de analizarlos en busca datos EXIF y otros metadatos, mostrándolos en pantalla.

### Importamos librerias
import argparse
import os
#from exif import Image
from PIL import Image
from PIL.ExifTags import TAGS
from prettytable import PrettyTable
import struct
import imghdr

### Declaracion de argumentos
parser = argparse.ArgumentParser(description= "Scorpion recibirá archivos de imagen como parámetros y será capaz de analizarlos en busca datos EXIF y otros metadatos, mostrándolos en pantalla.")
parser.add_argument("files", nargs = '+', default = [], help="Anade las imagenes para obtener sus metadatos EXIF")
arg = parser.parse_args()

### Propiedades
img_format = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg')

### Funciones
def get_metadata(image_name):

    image = Image.open(image_name)
    try:
        img_exif_data = image._getexif()
    except Exception:
        img_exif_data = False


    table = PrettyTable()
    table.field_names = ["Etiqueta", "Valor"]

    if img_exif_data:

        for id  in img_exif_data:
            tag_name = TAGS.get(id, id)
            data = img_exif_data.get(id)
            
            #if data in bytes
            try:
                if isinstance(data, bytes):
                    data = data.decode()

                table.add_row([tag_name, data])
            except Exception:
                x = 0

        print(table)
    
    else:
        if imghdr.what(image_name) == "bmp":
            bmp = open(image_name, 'rb')

            
            table.add_row(['Type', bmp.read(2).decode()])
            table.add_row(['Size', struct.unpack('I', bmp.read(4))])
            table.add_row(['Reserved 1', struct.unpack('H', bmp.read(2))])
            table.add_row(['Reserved 2', struct.unpack('H', bmp.read(2))])
            table.add_row(['Offset', struct.unpack('I', bmp.read(4))])

            table.add_row(['DIB Header Size', struct.unpack('I', bmp.read(4))])
            table.add_row(['Width', struct.unpack('I', bmp.read(4))])
            table.add_row(['Height', struct.unpack('I', bmp.read(4))])
            table.add_row(['Colour Planes', struct.unpack('H', bmp.read(2))])
            table.add_row(['Bits per Pixel', struct.unpack('H', bmp.read(2))])
            table.add_row(['Compression Method', struct.unpack('I', bmp.read(4))])
            table.add_row(['Raw Image Size', struct.unpack('I', bmp.read(4))])
            table.add_row(['Horizontal Resolution', struct.unpack('I', bmp.read(4))])
            table.add_row(['Vertical Resolution', struct.unpack('I', bmp.read(4))])
            table.add_row(['Number of Colours', struct.unpack('I', bmp.read(4))])
            table.add_row(['Important Colours', struct.unpack('I', bmp.read(4))])
        else:
            megapixels = (image.size[0]*image.size[1]/1000000) # Megapixels
            t = len(Image.Image.getbands(image)) # Number of channels

            table.add_row(['Filename', image.filename])
            table.add_row(['Format', image.format])
            table.add_row(['Number of Channels', t])
            table.add_row(['Mode', image.mode])
            table.add_row(['Palette', image.palette])
            table.add_row(['Width', image.size[0]])
            table.add_row(['Height', image.size[1]])
            table.add_row(['Megapixels', megapixels])

            print(table)

### Main
# Control inicial de errores
if len(arg.files) == 0:
    print("Syntax Error. Debes anadir los ficheros de los cuales obtener los metadatos EXIF")
else:
    for f_name in arg.files:
        if get_metadata(f_name) == -1:
            print("Image has no EXIF metadata")
