#encoding:utf-8


from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
from bs4 import BeautifulSoup

def scrape():
        for pag in range(1, 5):
            url = "https://www.elseptimoarte.net/estrenos/" + str(pag)
            f = urllib.request.urlopen(url)
            s = BeautifulSoup(f, "lxml")
            ul = s.find("ul", class_="elements")
            if not ul:
                continue
            lista_peliculas = ul.find_all("li")
            for item in lista_peliculas:
                pelicula_url = "https://www.elseptimoarte.net/" + item.a['href']
                f = urllib.request.urlopen(pelicula_url)
                s = BeautifulSoup(f, "lxml")
                aux = s.find("main", class_="informativo").find_all("section", class_="highlight")
                datos = aux[0].div.dl
                titulo_original = datos.find("dt", string="Título original").find_next_sibling("dd").string.strip()
                if datos.find("dt", string="Título"):
                    titulo = datos.find("dt", string="Título").find_next_sibling("dd").string.strip()
                else:
                    titulo = titulo_original
                paises = "".join(datos.find("dt", string="País").find_next_sibling("dd").stripped_strings)
                pais = paises.split(",")[0]
                estreno = datos.find("dt", string="Estreno en España").find_next_sibling("dd").string.strip()
                try:
                    fecha = datetime.strptime(estreno, '%d/%m/%Y')
                except ValueError:
                    fecha = estreno
                
                info = s.find("div", id="datos_pelicula")
                generos_text = "".join(info.find("p", class_="categorias").stripped_strings)
                generos = generos_text.split(",")
                directores_text = "".join(info.find("p", class_="director").stripped_strings)
                director = directores_text.split(",")[0]

                print("Título:", titulo)
                print("Título Original:", titulo_original)
                print("País:", pais)
                print("Fecha de Estreno:", fecha)
                print("Géneros:", generos)
                print("Director:", director)
                print("-" * 20)


if __name__ == "__main__":
    scrape()