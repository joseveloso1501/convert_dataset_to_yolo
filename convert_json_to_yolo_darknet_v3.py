# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
@author: Jose I. Veloso I.

ultima mejora: - obtiene los metadatos de las imagenes respectivas, y adapta el ancho y largo (h,w) de cada una para cada generar los archivo txt de etiquetas
"""

def main (args):   
    if len(sys.argv) == 4:
        import json
        import os
        import errno
        #import PIL 
        #import exifread    #pip install exifread
        #from PIL import Image, ExifTags
        from PIL import Image
        from PIL.ExifTags import TAGS         

        directorio = sys.argv[1]    #directorio que contiene las imagenes y el archivo con su respectivo etiquetado en formato json
        w_i = int(sys.argv[2])    #ancho de las imagenes
        h_i = int(sys.argv[3])    #alto de las imagenes 
        w = w_i
        h = h_i    #se asignan valores recibidos de ancho y alto a variables auxiliares 

        directorio = directorio.replace('\\', '/') + "/"    #se modifica el directorio para correcta lectura de python
        contenido_directorio = os.listdir(directorio)

        data = {}
        nombre_archivos_jpg = []   
        ejpg = '.jpg'
        ejson = '.json'
        etxt = '.txt'
        #archivo_json = 'berries.json'    #nombre del archivo que contiene el etiquetado original
        carpeta = 'labels_v9'        

        try:
            os.mkdir(directorio + carpeta)    #se crea una carpeta para almacenar todos los archivos de etiquetado creados
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        for archivo in contenido_directorio:
            if os.path.isfile(os.path.join(directorio, archivo)) and archivo.endswith(ejpg):
                nombre_archivos_jpg.append(archivo.replace(ejpg, ''))    #se obtienen los nombres de los archivos JPG encontrados y se almacenan en una lista, sin la extension '.jpg'
                #print("Archivo JPG encontrado: ", archivo)

        for archivo in contenido_directorio:
            if os.path.isfile(os.path.join(directorio, archivo)) and archivo.endswith(ejson):
                archivo_json = archivo    #se obtiene el nombre del primer archivo JSON encontrado y se almacena en la variable archivo_json
                #print("Archivo JSON encontrado: ", archivo)
                break
            
        etiquetas = directorio + archivo_json
        
        with open(etiquetas) as file:
            data = json.load(file)
        
            for nombre in nombre_archivos_jpg:    #para cada nombre almacenado en 'nombre_archivos_jpg', obtenidos a partir del dataset de imagenes
                puntos = []
                lineas = []
                archivo_txt = directorio + carpeta + '/' + nombre + etxt    #se genera un archivo '.txt' para almacenar el etiquetado en formato 'YOLO DARKNET TXT'
                imagen = nombre + ejpg    #imagen es el "objeto" a buscar en el json (nombre de la imagen, cuyo etiquetado esta contenido en el objeto)
                archivo_jpg = directorio + imagen    #ubicacion de cada imagen para lectura de metadatos
                #archivo_jpg = "IMG_1007.jpg"
                #print("archivo_jpg: ", archivo_jpg)
                image = Image.open(archivo_jpg)    #Lee la imagen en el directorio señalado
                exifdata = image.getexif() 

                for tagid in exifdata: 
                    tagname = TAGS.get(tagid, tagid) 
                    value = exifdata.get(tagid) 
                    if (tagname == "Orientation" and value == 1):    #si la orientacion de la imagen es horizontal
                        w = w_i
                        h = h_i
                    if (tagname == "Orientation" and value == 6):    #si la orientacion de la imagen es vertical
                        w = h_i
                        h = w_i
                    #print(f"{tagname:25}: {value}") 
                image.close()

                try:    #se usa try-except en caso de que no exista etiquetado en el json para alguna imagen del dataset
                    for objeto in data[imagen]:
                        puntos.append("0")    #se agrega a la lista un 0 (clase a la que pertenece el etiquetado), y luego todos los puntos del bounding box

                        punto_x = int(objeto['x'])    #los puntos obtenidos del archivo json se transforman a formato numerico
                        punto_y = int(objeto['y'])
                        punto_w = int(objeto['w'])
                        punto_h = int(objeto['h'])

                        bbox_w = (punto_w - punto_x)/w    #coordenadas normalizadas segun requerimientos de YOLO 
                        bbox_h = (punto_h - punto_y)/h
                        bbox_x = (punto_x/w + bbox_w/2)
                        bbox_y = (punto_y/h + bbox_h/2)

                        puntos.append(str("{0:.6f}".format(bbox_x)))    #se limita la cantidad de decimales en las coordenadas normalizadas 
                        puntos.append(str("{0:.6f}".format(bbox_y)))    #y se almacenan en una lista como string
                        puntos.append(str("{0:.6f}".format(bbox_w))) 
                        puntos.append(str("{0:.6f}".format(bbox_h))) 
                        
                        lineas.append(" ".join(puntos))    #la lista de puntos previa es un bounding box y este se almacenan en otra lista
                        puntos = []

                except KeyError:    #se controla excepcion en caso de que no exista etiquetado en json para alguna imagen del dataset
                    lineas = ""    #se eliminan los puntos almacenados del archivo anterior
                    archivo_txt = ""    #se elimina el nombre del archivo sin etiquetado
                    print("Error en: ", imagen)

                if archivo_txt != "":    #no se consideran los nombres de archivo sin etiquetado
                    print("======================================")
                    print("Imagen: ", archivo_jpg)                    
                    print("Lineas generadas (etiquetas): ")
                    with open(archivo_txt, "w") as file:
                        for linea in lineas:
                            print(linea)
                            file.write(linea + "\n")    #se escriben los puntos de los bounding box en el archivo '.txt'
                    print("Archivo de texto generado: ", archivo_txt)
                    print("======================================")
                    
                    WINDOWS_LINE_ENDING = b'\r\n'
                    UNIX_LINE_ENDING = b'\n'
                    with open(archivo_txt, 'rb') as open_file:
                        content = open_file.read()
                        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)    #conversion de formato de endline windows->unix
                    with open(archivo_txt, 'wb') as open_file:
                        open_file.write(content)
    else:
        print("Error: Faltan argumentos para ejecutar el script.")
        print("Uso correcto:>> python convert_json_to_yolo_darknet_v3.py 'ruta\dataset' ancho_imagenes alto_imagenes")
        #python convert_json_to_yolo_darknet_v3.py 'C:\Users\ignac\Documents\TESIS\img' 3264 2448
        #python convert_json_to_yolo_darknet_v3.py 'C:\Users\ignac\Documents\TESIS\IMG_1119' 1920 1080
        #python convert_json_to_yolo_darknet_v3.py 'C:\Users\ignac\Documents\TESIS\IMG_1120' 1920 1080
        #python convert_json_to_yolo_darknet_v3.py 'C:\Users\ignac\Documents\TESIS\IMG_1122' 1920 1080
        #python convert_json_to_yolo_darknet_v3.py 'C:\Users\ignac\Documents\TESIS\IMG_1123' 1920 1080

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
