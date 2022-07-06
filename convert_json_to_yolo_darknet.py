# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
@author: Jose I. Veloso I.
"""

def main (args):   
    if len(sys.argv) == 2:
        directorio = sys.argv[1] 
        directorio = directorio.replace('\\', '/') + "/"    #se modifica el directorio para correcta lectura de python
        
        import json
        import os
        import errno
        
        h = 2448 #alto
        w = 3264 #ancho, estos valores corresponden a un archivo de etiquetado cuya imagen esta en posicion horizontal
        
        archivo_json = 'berries.json'
        data = {}
        nombre_archivos = []
        #directorio = 'IMG_1119/'
        contenido_directorio = os.listdir(directorio)
        extension = '.jpg'
        carpeta = 'labels'        

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
                
                archivo_txt = directorio + carpeta + '/' + nombre + '.txt'    #se genera un archivo '.txt' para almacenar el etiquetado en formato 'YOLO DARKNET TXT'
                imagen = nombre + '.jpg'    #imagen es el objeto a buscar en el json (nombre de la imagen, cuyo etiquetado esta contenido en el objeto)
        
                try:    #se usa try-except en caso de que no exista etiquetado en el json para alguna imagen del dataset
                    
                    for point in data[imagen]:
                        puntos.append("\n0")    #se agrega a la lista un 0 (clase a la que pertenece el etiquetado), y luego todos los puntos del bounding box
                        '''
                        puntos.append(str(point['x']))
                        #print('x:', point['x'])
        
                        puntos.append(str(point['y']))
                        #print('y:', point['y'])
        
                        puntos.append(str(point['w']))
                        #print('w:', point['w'])
        
                        puntos.append(str(point['h']))
                        #print('h:', point['h'])
                        '''
                        puntos.append(str("{0:.6f}".format(int(point['x'])/w))) #coordenada X/W, normalizada segun requerimientos de YOLO 
                        puntos.append(str("{0:.6f}".format(int(point['y'])/h))) #coordenada y/H
                        puntos.append(str("{0:.6f}".format(int(point['w'])/w))) #coordenada w/W
                        puntos.append(str("{0:.6f}".format(int(point['h'])/h))) #coordenada h/H
                        linea_nueva = " ".join(puntos) 
                        
                except KeyError:    #se controla excepcion en caso de que no exista etiquetado en json para alguna imagen del dataset
                    linea_nueva = ""    #se eliminan los puntos almacenados del archivo anterior
                    archivo_txt = ""    #se elimina el nombre del archivo sin etiquetado
                    print("Error: ", imagen)            
                    
                puntos_agrupados = puntos_agrupados + linea_nueva    #los puntos obtenidos son dispuestos para almacenarlos en '.txt' correctamente
                
                print("================================================")
                print("archivo: ", archivo_txt)
                print("puntos: \n", puntos_agrupados)
                print("================================================")              
               
                if archivo_txt != "":    #no se consideran los nombres de archivo sin etiquetado
                    file = open(archivo_txt, "w")
                    file.write(puntos_agrupados)    #se escriben los puntos de los bounding box en el archivo '.txt'
                    file.close()

                    #conversion de formato windows -> unix
                    WINDOWS_LINE_ENDING = b'\r\n'
                    UNIX_LINE_ENDING = b'\n'
                    with open(archivo_txt, 'rb') as open_file:
                        content = open_file.read()
                        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
                        open_file.close()
                    with open(archivo_txt, 'wb') as open_file:
                        open_file.write(content)
                        open_file.close()
    else:
        print("Error: Faltan argumentos para ejecutar el script.")
        print("Uso correcto:>> python convert_json_to_yolo_darknet.py 'ruta_dataset'\n")
            
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
