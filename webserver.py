from functools import cached_property
#importar la libreria-----
import re #Se Importo RE para poder emplear las Expresiones Regulares en este codigo (Ejemplo: \d+)
import redis #Se Importo Redis para poder emplearlo
import uuid
import random
#--------------------------
from http.cookies import SimpleCookie #Servira para poder emplear las cookies
from http.server import BaseHTTPRequestHandler, HTTPServer #Clase de 29/02/2024
from urllib.parse import parse_qsl, urlparse #Librerias que procesa el valor 

# Código basado en:
# https://realpython.com/python-http-server/
# https://docs.python.org/3/library/http.server.html
# https://docs.python.org/3/library/http.cookies.html


#-------------------CLASE DE VIERNES Y LUNES 04 DE MARZO-------------
r = redis.StrictRedis(host="localhost", port = 6379, db = 0)
#redis_storage= redis.Redis()
#---------------------------------------------------------------------

mappings = [
    (r"^/books/book(?P<book_id>\d+).html$", "get_book"),
    (r"^/books/(?P<book_id>\d+)$", "get_book"),
    (r"^/book/(?P<book_id>\d+)$", "get_book"), 
    (r"^/$", "index"),
    (r"^/search", "search"),
    ]

#-------------------------------------------


class WebRequestHandler(BaseHTTPRequestHandler):
    
    @property
    def query_data(self):
        return dict(parse_qsl(self.url.query))
    @property
    def url(self):#Si deseamos el URL
        return urlparse(self.path) 
        
    def search(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        index_page = f"<h1>{self.query_data['q'].split()}</h1>".encode("utf-8")
        self.wfile.write(index_page)
        
    def cookies(self):
        return SimpleCookie(self.headers.get('Cookie'))
    
    def get_session(self):
#        cookies = self.cookies()
#	    return uuid.uuid4() if not cookies else cookies["session_id"].value
        
        session_id = None #Inicializamos la session nulo
        cookies = self.cookies()
        #return uuid.uuid4() <--------------
        if not cookies:#Si no hay cookies
            session_id = uuid.uuid4() #Se le crea uno con UUID
        else:
            session_id = cookies["session_id"].value
        return session_id
    
    def write_session_cookie(self, session_id):
        cookies = SimpleCookie()
        cookies["session_id"] = session_id
        cookies["session_id"]["max-age"] = 1000 #Para determinar el tiempo en el que la cookie se le asigna a la session
        self.send_header("Set-Cookie", cookies.output(header=""))#Se mandaran las cookies pero sin ENCABEZADO

    
# CLASE 28/02/2024 y 29/02/2024--------------------
    def do_GET(self):
        #match = self.get_params("^/books/(?P<book_id>\d+)$",self.path)
        #if match:
        #    self.get_book(match["book_id"])
        #else:
        #    self.wfile.write(f"<h1> El path {self.path} es INCORRECTO </h1>".encode("utf-8"))
        self.url_mapping_response()
    
    def url_mapping_response(self):
        for parrent, method in mappings:
            params = self.get_params(parrent, self.path)
            if params is not None:
                md = getattr(self, method)
                md(**params)
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write("Not Found".encode("utf-8"))

    
    def get_params(self, pattern, path):
       match = re.match(pattern, path)
       if match:
           return match.groupdict()
#       else:
#           return None
        
    def index(self):
        session_id = self.get_session()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.write_session_cookie(session_id)
        self.end_headers()
        index_page = """
        <CENTER><h1>¡Bienvenidos a los libros!</h1>
            <form action="/search" method="GET">
                <label for="q">Search</label>
                <input type ="text" name="q"/>
                <input type ="submit" value="Buscar libros">
            </form>
        </CENTER>
        """.encode("utf-8")
        self.wfile.write(index_page)
        
        try:
            self.wfile.write(self.show_all_books().encode("utf-8"))
        except TypeError:
            self.wfile.write('<p>Error mostrando libros</p>'.encode('utf-8'))
    
    def show_all_books(self):
        session_id = self.get_session()
        self.end_headers()
        with open('html/index.html') as f:
            response = f.read()
        self.wfile.write(response.encode("utf-8"))
        
        
    def get_book(self, book_id):
        session_id = self.get_session()
        book_recommend = self.recommend_book(session_id, book_id)
        r.lpush(f"session:{session_id}", f"book:{book_id}")
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.write_session_cookie(session_id)
        self.end_headers()
        
        book_info = r.get(f'book:{book_id}')
        self.wfile.write(f'Book ID:{book_id}\n'.encode('utf-8'))
        
        if book_info is not None:
            self.wfile.write(f'Book Info:{book_info.decode("utf-8")}\n'.encode('utf-8'))
        else:
             self.wfile.write(f"""<h1>No existe libro</h1>
             <p>  Recomendación: Libro:{book_recommend}</p>\n""".encode('utf-8'))
            
        book_list = r.lrange(f'session:{session_id}', 0, -1)
        
        for book in book_list:
            self.wfile.write(f'Book:{book.decode("utf-8")}\n'.encode('utf-8'))
#---------------------------------------------------------------------------------------------------            
            
    def recommend_book(self, session_id, book_id):
        r.rpush(session_id, book_id)
        books = r.lrange(session_id, 0, 7)
        print(session_id, books)
        all_books = [str(i+1) for i in range(6)]
        new = [b for b in all_books if b not in
               [vb.decode() for vb in books]]
        if new:
            return new[0]
    
    
if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
#------------------------------------------------------------------------------------
