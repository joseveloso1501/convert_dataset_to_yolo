# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
@author: Jose I. Veloso I.
"""

def main (args):   
    if len(sys.argv) == 4:
        import json
        import os
        from PIL import Image
        from PIL.ExifTags import TAGS     
        from pathlib import Path

        directorio = sys.argv[1]    #directorio que contiene las imagenes y el archivo con su respectivo etiquetado en formato json
        w_i = int(sys.argv[2])    #ancho de las imagenes
        h_i = int(sys.argv[3])    #alto de las imagenes 
        archivo_json_v2 = 'berries_v9.json'    #nuevo archivo json que contendra las etiquetas de los bounding box en formato original
        
        w = w_i
        h = h_i    #se asignan valores recibidos de ancho y alto a variables auxiliares 

        directorio = directorio.replace('\\', '/') + "/"    #se modifica el directorio para correcta lectura de python
        contenido_directorio = os.listdir(directorio)
        print("Directorio de etiquetas: \n", directorio)   
        print("Contenido del directorio: \n", contenido_directorio)   

        directorio_p = str(Path(directorio).parents[0])+ "/"    #se accede al directorio padre el que contiene el archivo JSON con etiquetas original
        contenido_directorio_p = os.listdir(directorio_p)
        print("Directorio de dataset con archivo JSON: \n", directorio_p)   
        print("Contenido del directorio: \n", contenido_directorio_p)   

        #archivo_json = 'berries.json'

        data = {}
        data_v2 = {}
        nombre_archivos_jpg = []    
        nombre_archivos_json = []
        elementos_linea = []    
        etxt = '.txt'
        ejpg = '.jpg'  
        ejson = '.json'
        #carpeta = '/labels_v8'    #carpeta que contiene las etiquetas
        count = 0     #contador de bounding boxes
        similitud = 0    #similitud promedio de etiquetas originales vs las generadas en este script

        for archivo in contenido_directorio:
            if os.path.isfile(os.path.join(directorio, archivo)) and archivo.endswith(etxt):
                nombre_archivos_jpg.append(archivo.replace(etxt, ''))    #se obtienen los nombres de los archivos y se almacenan sin la extension '.jpg'
                print("Archivo TXT encontrado: ", archivo)    #se comprueba el nombre de los archivos seleccionados

        for archivo in contenido_directorio_p:
            if os.path.isfile(os.path.join(directorio_p, archivo)) and archivo.endswith(ejson):
                archivo_json = archivo    #se obtienen los nombres de los archivos y se almacenan sin la extension '.jpg
                print("Archivo JSON encontrado: ", archivo)    #se comprueba el nombre de los archivos seleccionados
                break    #se obtiene el primer archivo .json encontrado

        etiquetas = directorio_p + archivo_json
        etiquetas_v2 = directorio_p + archivo_json_v2

        print("\nArchivos analizados: ")
        for nombre in nombre_archivos_jpg:    #########    #para cada nombre almacenado en 'nombre_archivos_jpg', obtenidos a partir del dataset de imagenes
            archivo_txt = directorio + nombre + etxt  ##########
            imagen = nombre + ejpg  ##########
            data_v2[imagen] = []
            archivo_jpg = directorio_p + imagen    #ubicacion de cada imagen para lectura de metadatos

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

            with open(archivo_txt) as txt:
                for linea in txt:
                    elementos_linea = linea.split()
                    #print("elementos_linea: ", elementos_linea)

                    bbox_x = float(elementos_linea[1])
                    bbox_y = float(elementos_linea[2])
                    bbox_w = float(elementos_linea[3])
                    bbox_h = float(elementos_linea[4])

                    punto_x_v2 = w*(bbox_x - (bbox_w/2))
                    punto_y_v2 = h*(bbox_y - (bbox_h/2))
                    punto_w_v2 = punto_x_v2 + w*bbox_w
                    punto_h_v2 = punto_y_v2 + h*bbox_h
                    #print("nueva linea: ", punto_x_v2, punto_y_v2, punto_w_v2, punto_h_v2) 

                    data_v2[imagen].append({
                        'x': round(punto_x_v2),
                        'y': round(punto_y_v2),
                        'w': round(punto_w_v2),
                        'h': round(punto_h_v2)})
                print(" ", archivo_txt)

        with open(etiquetas_v2, 'w') as file:
            json.dump(data_v2, file, indent=4)
            print("\nSe han convertido los archivos .txt al formato de etiquetado original y se han almacenado en: ")
            print(etiquetas_v2)
        
        with open(etiquetas) as file, open(etiquetas_v2) as file_2:
            data = json.load(file)
            data_v2 = json.load(file_2)
        
            for nombre in nombre_archivos_jpg:    #para cada nombre almacenado en 'nombre_archivos_jpg', obtenidos a partir del dataset de imagenes
                imagen = nombre + ejpg    #imagen es el "objeto" a buscar en el json (nombre de la imagen, cuyo etiquetado esta contenido en el objeto)

                for objeto in data[imagen]:
                    punto_x = int(objeto['x'])    #los puntos obtenidos del archivo json se transforman a formato numerico
                    punto_y = int(objeto['y'])
                    punto_w = int(objeto['w'])
                    punto_h = int(objeto['h'])

                for objeto_2 in data_v2[imagen]:
                    punto_x_2 = int(objeto_2['x'])    #los puntos obtenidos del archivo json se transforman a formato numerico
                    punto_y_2 = int(objeto_2['y'])
                    punto_w_2 = int(objeto_2['w'])
                    punto_h_2 = int(objeto_2['h'])

                if punto_x != punto_x_2:
                    similitud = similitud + (100*(punto_x_2/punto_x))
                else:
                    similitud = similitud + 100

                if punto_y != punto_y_2:
                    similitud = similitud + (100*(punto_y_2/punto_y))
                else:
                    similitud = similitud + 100

                if punto_w != punto_w_2:
                    similitud = similitud + (100*(punto_w_2/punto_w))
                else:
                    similitud = similitud + 100

                if punto_h != punto_h_2:
                    similitud = similitud + (100*(punto_h_2/punto_h))
                else:
                    similitud = similitud + 100
                count = count + 4
            
            similitud = round((similitud / count), 1)
            print("\nComparando '", etiquetas, "' con '", etiquetas_v2, "'")
            print("\nLas etiquetas convertidas son ", similitud, "%", " similares a las del archivo de etiquetas .json original.")
    else:
        print("Error: Faltan argumentos para ejecutar el script.")
        print("Uso correcto:>> python comparador.py 'ruta\dataset\etiquetas' ancho_imagenes alto_imagenes")
        #python comparador.py 'C:\Users\ignac\Documents\TESIS\img\labels_v7' 3264 2448
        #python comparador.py 'C:\Users\ignac\Documents\TESIS\IMG_1119\labels_v7' 1920 1080
        #python comparador.py 'C:\Users\ignac\Documents\TESIS\IMG_1120\labels_v7' 1920 1080
        #python comparador.py 'C:\Users\ignac\Documents\TESIS\IMG_1122\labels_v7' 1920 1080
        #python comparador.py 'C:\Users\ignac\Documents\TESIS\IMG_1123\labels_v7' 1920 1080

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
