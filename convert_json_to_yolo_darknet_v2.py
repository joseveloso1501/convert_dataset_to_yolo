# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
@author: Jose I. Veloso I.

ultima mejora: - se agrega la conversion a formato yolo con cifras normalizadas
               - se agrega cada linea de puntos obtenida y normalizada directamente al archivo txt
"""

def main (args):   
    if len(sys.argv) == 2:
        import json
        import os
        import errno

        #directorio = 'IMG_1119/'
        directorio = sys.argv[1] 
        directorio = directorio.replace('\\', '/') + "/"    #se modifica el directorio para correcta lectura de python
        contenido_directorio = os.listdir(directorio)

        w = 2448 #ancho w
        h = 3264 #alto h, estos valores corresponden a un archivo de etiquetado cuya imagen esta en posicion horizontal

        archivo_json = 'berries.json'
        data = {}
        nombre_archivos = []        
        extension = '.jpg'
        carpeta = 'labels_v2'        

        try:
            os.mkdir(directorio + carpeta)    #se crea una carpeta para almacenar todos los archivos de etiquetado creados
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        for archivo in contenido_directorio:
            if os.path.isfile(os.path.join(directorio, archivo)) and archivo.endswith(extension):
                nombre_archivos.append(archivo.replace(extension, ''))    #se obtienen los nombres de los archivos y se almacenan sin la extension '.jpg'
        '''
        for archivo in nombre_archivos: 
            #se comprueba el nombre de los archivos seleccionados
            print("Nombre_archivo: ", archivo)
        '''    
        etiquetas = directorio + archivo_json
        
        with open(etiquetas) as file:
            data = json.load(file)
        
            for nombre in nombre_archivos:    #para cada nombre almacenado en 'nombre_archivos', obtenidos a partir del dataset de imagenes
                
                puntos = []
                puntos_agrupados = ""
                lineas = []
                archivo_txt = directorio + carpeta + '/' + nombre + '.txt'    #se genera un archivo '.txt' para almacenar el etiquetado en formato 'YOLO DARKNET TXT'
                imagen = nombre + '.jpg'    #imagen es el objeto a buscar en el json (nombre de la imagen, cuyo etiquetado esta contenido en el objeto)
                
                try:    #se usa try-except en caso de que no exista etiquetado en el json para alguna imagen del dataset
                    for objeto in data[imagen]:
                        puntos.append("0")    #se agrega a la lista un 0 (clase a la que pertenece el etiquetado), y luego todos los puntos del bounding box
                        '''
                        puntos.append(str(objeto['x']))
                        #print('x:', objeto['x'])
        
                        puntos.append(str(objeto['y']))
                        #print('y:', objeto['y'])
        
                        puntos.append(str(objeto['w']))
                        #print('w:', objeto['w'])
        
                        puntos.append(str(objeto['h']))
                        #print('h:', objeto['h'])
                        '''
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
                    print("Error: ", imagen)

                print("================================================")
                print("archivo: ", archivo_txt)
                print("lineas: ")
                
                if archivo_txt != "":    #no se consideran los nombres de archivo sin etiquetado
                    file = open(archivo_txt, "w")
                    for linea in lineas:
                        print(linea)
                        file.write(linea + "\n")    #se escriben los puntos de los bounding box en el archivo '.txt'
                    file.close()
                    print("================================================")

                    WINDOWS_LINE_ENDING = b'\r\n'
                    UNIX_LINE_ENDING = b'\n'
                    with open(archivo_txt, 'rb') as open_file:
                        content = open_file.read()
                        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)    #conversion de formato de endline windows->unix
                        open_file.close()
                    with open(archivo_txt, 'wb') as open_file:
                        open_file.write(content)
                        open_file.close()
    else:
        print("Error: Faltan argumentos para ejecutar el script.")
        print("Uso correcto:>> python convert_json_to_yolo_darknet_v2.py 'ruta_dataset'\n")
        #python convert_json_to_yolo_darknet_v2.py ''
        #python convert_json_to_yolo_darknet_v2.py 'C:\Users\ignac\Documents\TESIS\img'
        #python convert_json_to_yolo_darknet_v2.py 'C:\Users\ignac\Documents\TESIS\IMG_1123'

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
