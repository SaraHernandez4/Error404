import os #Se Importo OS que es para hacer comandos del sistema operativo
import re #Se Importo RE para poder emplear las Expresiones Regulares en este codigo (Ejemplo: \d+)
import redis #Se Importo Redis para poder emplearlo
from bs4 import BeautifulSoup


r = redis.StrictRedis(host="localhost", port=6379, db=0)

def load_dir(path):
    #Loads the directory
    files = os.listdir(path)
    #Filter the files
    print(files)
    for f in files:
        match = re.match(r"^book(\d+).html$", f)
        if match is not None:
            with open(path + f) as file:
                html = file.read()
                book_id = match.group(1)
                r.set(f"book:{book_id}" , html)
                print(f"{file} loaded into Redis")

            
def create_index(book_id, html):
    soup = BeautifulSoup(html,'html.parser')
    ts = soup.get_text().split()
    for t in ts:
        r.sadd(t,book_id)

load_dir("html/books/")#Este PATH Lee los libros que estan dentro del directorio html; Y dentro de este esta books

