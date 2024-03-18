import os #Se Importo OS que es para hacer comandos del sistema operativo
import re #Se Importo RE para poder emplear las Expresiones Regulares en este codigo (Ejemplo: \d+)
import redis #Se Importo Redis para poder emplearlo
from bs4 import BeautifulSoup #Se importa la clase BeautifulSoup del paquete bs4 para el análisis de HTML y XML en Python.


r = redis.StrictRedis(host="localhost", port=6379, db=0) # Este código crea una instancia de conexión a una base de datos Redis en el servidor local, en el puerto 6379 y utilizando la base de datos 0.

def load_dir(path):
    #Loads the directory
    files = os.listdir(path) #  Obtiene una lista de nombres de archivos en el directorio especificado por path utilizando la función listdir del módulo os.
    #Filter the files
    print(files) #  Imprime los nombres de los archivos en el directorio.
    for f in files:# Itera sobre cada nombre de archivo en la lista files.
        match = re.match(r"^book(\d+).html$", f) #Busca un patrón específico en el nombre del archivo utilizando una expresión regular. 
        #El patrón busca archivos que comiencen con "book", seguido de uno o más dígitos, y terminen con ".html".
        if match is not None: #Verifica si se encontró una coincidencia entre el nombre del archivo y el patrón de expresión regular.
            with open(path + f) as file:# Abre el archivo encontrado en modo lectura.
                html = file.read()# Lee el contenido del archivo HTML en una variable llamada html.
                book_id = match.group(1)# Extrae el número de libro de la coincidencia utilizando el primer grupo capturado en la expresión regular.
                r.set(f"book:{book_id}" , html)# Almacena el contenido HTML del libro en Redis utilizando una clave que sigue el formato book:<book_id>.
                print(f"{file} loaded into Redis")# Imprime un mensaje indicando que el archivo ha sido cargado en Redis.

            
def create_index(book_id, html):
    soup = BeautifulSoup(html,'html.parser')#  Utiliza BeautifulSoup para analizar el HTML y crear un objeto soup que representa la estructura del documento HTML.
    ts = soup.get_text().split()# Extrae el texto del documento HTML y lo divide en una lista de palabras individuales.
    for t in ts:# Itera sobre cada palabra en la lista de palabras extraídas.
        r.sadd(t,book_id)# Agrega el book_id a un conjunto (utilizando Redis, dado que se usa la sintaxis r.sadd) asociado con cada palabra t, lo que sugiere la construcción de un índice donde cada palabra clave está asociada con el identificador del libro que la contiene.

load_dir("html/books/")#Este PATH Lee los libros que estan dentro del directorio html; Y dentro de este esta books

