from functools import cached_property
import re #Se Importo RE para poder emplear las Expresiones Regulares en este codigo (Ejemplo: \d+).
import redis #Se Importa un almacen donde yacen los libros empleados tipo html.
import uuid #Se importa un creador de ID para las sessiones.
from http.cookies import SimpleCookie #Se Importa las Cookies que son pequeña información enviada por un sitio web y almacenada en el navegador del usuario.
from http.server import BaseHTTPRequestHandler, HTTPServer #----
from urllib.parse import parse_qsl, urlparse #Se importa el convertidor de URL para que lo pueda mostrar como un dato legible.
import random #Se importa random de forma random.
from bs4 import BeautifulSoup #Se Importa la Hermosa Sopa para extraer datos de documentos HTML y XML y buscar coincidencias.
import json #Se Importa el JSON para buscar las palabras comunes de los archivos. De forma random es empleada.

#El MAPPINGS son creadas por expresiones regulares en las que se puede crear y desarrollar el URL mostrado
mappings = [
    (r"^/book/(?P<book_id>\d+)$", "get_book"),# Ejemplo: http://44.219.130.81:8000/book/1
    (r"^/books/(?P<book_id>\d+)$", "get_book"),# Ejemplo: http://44.219.130.81:8000/books/2
    (r"^/$", "index"),# Ejemplo: http://44.219.130.81:8000/
    (r"^/search", "search"), # Ejemplo: http://44.219.130.81:8000/search?q=hola+mudno
]

r = redis.StrictRedis(host="localhost", port=6379, db=0)# Se emplea para poder emplear el contenido de los libros en get_book y recommend_book.

class WebRequestHandler(BaseHTTPRequestHandler):# Clase
    
    def search(self):#El Método Search sirve para poder buscar y acceder a los libros por medio del Index
        self.send_response(200)# Envía una respuesta al cliente con el código de estado 404, que indica que el recurso solicitado no fue encontrado en el servidor.
        self.send_header("Content-Type", "text/html")# Finaliza la cabecera de la respuesta HTTP, indicando que no habrá más cabeceras.
        self.end_headers()# Escribe en el flujo de salida (wfile) del cliente el mensaje "Not Found", codificado en UTF-8 para asegurar que se transmita correctamente.
        
        query = self.query_data.get('q', '') # Es la variable obtenida por formulario de búsqueda.
        index_page = f"<h>q: {query.split()}</h1>".encode("utf-8")# Aquí las palabras ingresabas en el textbox son separadas para su búsqueda.
        self.wfile.write(index_page) # Esta función imprime lo seleccionado en la página web.
    
        with open('html/index.html') as f: # Esta función sirve para poder abrir un archivo html. 
            html_content = f.read() # En esta parte lee lo que abrio anteriormente, en este caso el index.html.
    
        soup = BeautifulSoup(html_content, 'html.parser') #Aquí se le asigna a una variable en contenido del html.
        h2_elements = soup.find_all('h2')  # Aquí almacena y Busca todos los elementos <h2></h2>.
    
        matching_books = [] # Aquí se crea una lista para almacenar todos los resultados similares de la búsqueda.
        for h2_element in h2_elements: # Aquí se emplea un bucle para mostrar y manipular los resultados almacenados.  
            a_element = h2_element.find('a')  # Aquí se Busca todo elemento <a> dentro de cada elemento <h2>.
            if a_element: # Sí se encontró elementos <a> dentro de <h2> entonces: ...
                title = a_element.text.lower()  # Se empleará una variable para ALMACENAR y OBTENER el TITULO en texto y poner todo en MINUSCULAS.
                link = a_element['href']  # Se empleará una variable para ALMACENAR y OBTENER el LINK en texto.
                if query.lower() in title: #Si el QUERY (en MINUSCULAS) aparece en el TITULO entonces: ...
                    matching_books.append(f"<a href='{link}'>{title}</a>") # Se almacenará tanto el TÍTULO como el LINK para mostrarlos en la WEB.
    
        if matching_books:# Sí se encontro elementos similares entonces ...
            response_content = "<h1>Libros encontrados:</h1>" # Se imprimira "Libros encontrados"
            response_content += "<ul>"# BRINCO
            response_content += "".join([f"<li>{book}</li>" for book in matching_books])# Se imprimira "El nombre del libro y el link"
            response_content += "</ul>"# CIERRE DE BRINCO
        else:# Sí no se encontro similitudes en los libros entonces:...
            response_content = "<p>No se encontraron libros que coincidan con la búsqueda.</p>" # Se imprimira esto: "No se encontraron libros que coincidan con la búsqueda
    
        self.wfile.write(response_content.encode('utf-8')) # Esta función imprime lo seleccionado en la página web.
        
    def get_session(self): # El Método get_session crea la sessión del usuario del navegador por medio de Cookies.
        cookies = self.cookies # Aquí se le asigna a una variables la Cookie CREADA al iniciar la página web.
        session_id = None # Aquí se inicializa una variable que servira como sessión y determinante sí el usuario es nuevo en la página web.
        if 'session_id' not in cookies: # Sí la session_id no esta con alguna cookie entonces: ...
            session_id = str(uuid.uuid4()) # Se GENERA una Cookies o ID de usuario y se le asigna a la variable.
        else: # En otro caso: ...
            session_id = cookies['session_id'].value # Se ASIGNA y GUARDA el ID del usuario de navegador.
        return session_id # Aquí se REGRESA el ID/COOKIE del usuario.

    def write_session_cookie(self, session_id):# El Método write_session_cookies guarda y muestra la cookie del usuario navegador
        cookies = SimpleCookie()#Crea un objeto SimpleCookie, que es una clase proporcionada por el módulo http.cookies de Python. Esto se utiliza para manejar cookies HTTP.
        cookies['session_id'] = str(session_id)# Establece el valor de la cookie con clave 'session_id' como el valor de session_id convertido a una cadena de caracteres.
        cookies['session_id']['max-age'] = 1000#Establece la duración máxima de la cookie 'session_id' en segundos. En este caso, la cookie expirará después de 1000 segundos (aproximadamente 16 minutos).
        self.send_header('Set-Cookie', cookies.output(header=''))#Envía un encabezado HTTP Set-Cookie al cliente (navegador web) con la información de la cookie. La función send_header envía respuestas al cliente.

    @property
    def cookies(self):# Este Método Retorna un objeto SimpleCookie creado a partir de los datos de la cabecera 'Cookie' de la solicitud HTTP. 
        return SimpleCookie(self.headers.get('Cookie', ''))# Sí no se encuentra ninguna cookie en la cabecera, se pasa una cadena vacía como valor predeterminado.
        
    @property
    def query_data(self):# Este Método Retorna un diccionario que contiene los datos de la consulta en la URL. 
        return dict(parse_qsl(self.url.query))# Utiliza la función parse_qsl del módulo urllib.parse para analizar la cadena de consulta (query) de la URL y devuelve una lista de tuplas de pares clave-valor.
        # Luego, se convierte esta lista en un diccionario mediante la función dict().
        
    @property
    def url(self):# Este Método Utiliza la función urlparse para analizar la ruta (path) de la solicitud HTTP.
        return urlparse(self.path)# Devuelve un objeto que contiene diferentes componentes de la URL, como el esquema, el host, el camino, etc.

    def do_GET(self): #Este Método llama a otro Método
        self.url_mapping_response()

    def get_params(self, pattern, path):# Este Método Crea y Obtiene los parámetros
        match = re.match(pattern, path)# Retorna un objeto de coincidencia si se encuentra una coincidencia, o None si no hay coincidencias.
        if match:# Comprueba si se encontró una coincidencia en la cadena.
            return match.groupdict()# Si hay una coincidencia, devuelve un diccionario que contiene los grupos de captura definidos en el patrón de expresión regular.

    def url_mapping_response(self):# Este Método Regresará los URL creados
        for (pattern, method) in mappings:# Itera sobre una lista de tuplas llamada mappings, donde cada tupla contiene un patrón de URL y un método asociado.
            match = self.get_params(pattern, self.path) #Utiliza el método get_params para intentar hacer coincidir el patrón de URL con la ruta actual (self.path). 
            #Retorna un diccionario con los parámetros coincidentes si hay una coincidencia, o None si no hay coincidencia.
            
            if match is not None:# Verifica si se encontró una coincidencia entre el patrón de URL y la ruta actual.
                md = getattr(self, method)#  Obtiene el método asociado con la coincidencia del patrón de URL, utilizando getattr() para obtener un atributo de la instancia de la clase actual.
                md(**match)# Llama al método obtenido anteriormente con los parámetros coincidentes que se encontraron.s
                return# Termina la ejecución del método después de manejar la primera coincidencia entre el patrón de URL y la ruta actual.

        self.send_response(404) #Envía una respuesta al cliente con el código de estado 404, que indica que el recurso solicitado no fue encontrado en el servidor.
        self.end_headers()# Finaliza la cabecera de la respuesta HTTP, indicando que no habrá más cabeceras.
        self.wfile.write('Not Found'.encode('utf-8'))# Escribe en el flujo de salida (wfile) del cliente el mensaje "Not Found", codificado en UTF-8 para asegurar que se transmita correctamente.

    def index(self):# Este Método maneja la página principal y contiene el Formulario de Búsqueda
        self.send_response(200)# Envía una respuesta HTTP con el código de estado 200, indicando que la solicitud fue exitosa.
        self.send_header("Content-Type", "text/html")# Agrega un encabezado HTTP indicando que el tipo de contenido de la respuesta es HTML.
        self.end_headers()# Finaliza la cabecera de la respuesta HTTP, indicando que no habrá más cabeceras.
        
        #index_page = """...""".encode("utf-8"):
        #Crea una cadena de texto con el contenido HTML de la página principal y la codifica en UTF-8 para ser enviada como bytes.
        index_page = """
        <CENTER><h1>¡Bienvenidos a los libros!</h1>
            <form action="/search" method="GET">
                <label for="q">Search</label>
                <input type ="text" name="q"/>
                <input type ="submit" value="Buscar libros">
            </form>
        </CENTER>
        """.encode("utf-8")
        self.wfile.write(index_page)# Escribe el contenido de la página principal en el flujo de salida del servidor para ser enviado al cliente.
        self.wfile.write(self.show_all_books().encode("utf-8"))#  Llama a un método show_all_books() que probablemente devuelve una lista de libros
        #la escribe en el flujo de salida del servidor, también codificada en UTF-8.

    def get_book(self, book_id):# Este Método sirve para localizar los libros por medio de book/#
        session_id = self.get_session()# Obtiene el identificador de sesión del usuario.
        book_recommend = self.recommend_book(session_id, book_id)# Genera una recomendación de libro para el usuario basada en su sesión y el libro solicitado.
        r.lpush(f'session:{session_id}', f'book:{book_id}')# Agrega el libro consultado recientemente a la lista de libros consultados en la sesión del usuario.
        self.send_response(200)# Envía una respuesta HTTP 200 (OK) al cliente. 
        self.send_header('Content-Type', 'text/html')# Envía el encabezado HTTP Content-Type con el tipo de contenido como text/html.
        self.write_session_cookie(session_id)# Escribe una cookie de sesión para el usuario.
        self.end_headers()# Finaliza los encabezados HTTP de la respuesta.
        book_info = r.get(f'book:{book_id}')#  Obtiene la información del libro solicitado desde algún lugar (presumiblemente una base de datos o algún almacenamiento en caché).
        self.wfile.write(f'Book ID: {book_id}\n'.encode('utf-8')) #Escribe el ID del libro en el flujo de salida de la respuesta HTTP.
        
        if book_info is not None:#Si book_info tiene información, muestra la información del libro.
            self.wfile.write(f'Book Info: {book_info.decode("utf-8")}\n'.encode('utf-8'))
        else:#Si no, muestra un mensaje indicando que el libro no existe junto con una recomendación de libro alternativo.
            self.wfile.write(f"""<h1>No existe libro</h1>
             <p>  Recomendacion: Libro {book_recommend}</p>\n""".encode('utf-8'))
            
        book_list = r.lrange(f'session:{session_id}', 0, -1)# Obtiene la lista de libros consultados recientemente en la sesión del usuario.
        for book in book_list:# Itera sobre book_list y escribe cada libro en el flujo de salida de la respuesta HTTP.
            self.wfile.write(f'Book: {book.decode("utf-8")}\n'.encode('utf-8'))
    
    def show_all_books(self):# Este Método muestra los libros en el Indice/Página Principal que estan almacenados.
        self.end_headers()# Finaliza la escritura de los encabezados de la respuesta HTTP. Esto indica que no habrá más encabezados en la respuesta.
        with open('html/index.html') as f:# Abre el archivo 'index.html' ubicado en el directorio 'html' en modo de lectura y lo asigna al identificador 'f'. La sentencia with asegura que el archivo se cierre correctamente después de su uso.
            response = f.read()# Lee el contenido del archivo 'index.html' y lo almacena en la variable 'response'.
        self.wfile.write(response.encode("utf-8"))# Escribe el contenido de 'response' en el flujo de salida de la respuesta HTTP (wfile) codificado en UTF-8. 
        #Esto envía el contenido del archivo 'index.html' como parte de la respuesta HTTP al cliente.
    
    def recommend_book(self, session_id, book_id):# Este Método muestra las recomendaciones de Libros cuando no se encuentra un LIBRO
        r.rpush(session_id, book_id)# Agrega el book_id al final de una lista asociada con la session_id. 
        books = r.lrange(session_id, 0, 7)# Obtiene una lista de hasta 8 libros vistos más recientemente por el usuario a partir de la lista asociada con session_id.
        all_books = set(str(i+1) for i in range(6))# Crea un conjunto de cadenas de texto que representan los identificadores de todos los libros disponibles (del 1 al 6).
        new = [b for b in all_books if b not in [vb.decode() for vb in books]]# Encuentra los libros que el usuario aún no ha visto comparando los identificadores de todos los libros con los identificadores de los libros que ha visto el usuario.
        if new:# Comprueba si hay libros nuevos para recomendar.
            return new[0]# Devuelve el primer libro nuevo encontrado para recomendar.
        else:#  Si no hay libros nuevos para recomendar.
            return random.choice([vb.decode() for vb in books]) # Elige aleatoriamente un libro que el usuario haya visto anteriormente y lo devuelve como recomendación.

if __name__ == "__main__":# Verifica si el script está siendo ejecutado directamente como un programa independiente y no está siendo importado como un módulo en otro script.
    print("Server starting...") #Imprime un mensaje en la consola indicando que el servidor está empezando a ejecutarse.
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler) #Crea una instancia de HTTPServer que escucha en todas las interfaces de red ("0.0.0.0") en el puerto 8000. 
    #WebRequestHandler es una clase que maneja las solicitudes HTTP entrantes.
    server.serve_forever()#Inicia el servidor y lo pone en un bucle infinito para manejar continuamente las solicitudes entrantes hasta que se detenga manualmente o ocurra algún error.