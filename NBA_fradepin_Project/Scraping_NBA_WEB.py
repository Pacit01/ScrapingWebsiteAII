# encoding:utf-8

from bs4 import BeautifulSoup
import requests
import urllib.request
import lxml
import re  # Importa la librería para expresiones regulares
import socket  # Importa la librería socket

# Variables globales para almacenar los datos
player_award_counts = {}  # Diccionario global para almacenar el conteo de premios por jugador
award_urls = {}  # Diccionario global para almacenar las URLs de los premios


def scrape_award_urls_from_strong_tags(main_url, specific_awards):
    """
    Extrae las URLs de los premios de la NBA desde la página principal de premios.

    Args:
        main_url (str): La URL de la página principal de premios.
        specific_awards (list): Una lista de nombres de premios específicos para extraer URLs.

    Returns:
        dict: Un diccionario donde las claves son los nombres de los premios y los valores son sus URLs.
              Retorna None si ocurre algún error.
    """
    global award_urls  # Indica que estamos usando la variable global
    try:
        response = requests.get(main_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        award_links = {}
        article_content = soup.find('div', class_='ArticleContent_article__NBhQ8')

        if article_content:
            strong_tags_with_links = article_content.find_all('strong')
            for strong_tag in strong_tags_with_links:
                link_tag = strong_tag.find('a', href=True)
                if link_tag:
                    award_name = link_tag.text.strip()
                    if award_name in specific_awards:  # Verifica si el premio está en la lista específica
                        award_url = f"https://www.nba.com{link_tag['href']}"
                        award_links[award_name] = award_url
        award_urls = award_links  # Asigna a la variable global
        return award_links

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the main URL: {e}")
        return None
    except AttributeError:
        print("Error parsing the HTML structure of the main page.")
        return None


def scrape_award_winners(url, award_name):
    """
    Realiza web scraping de la página dada para extraer información sobre los ganadores de un premio de la NBA.

    Args:
        url (str): La URL de la página web a scrapear.
        award_name (str): El nombre del premio (ej., "MVP", "Rookie of the Year").

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa a un ganador del premio y contiene su 'año', 'jugador' y 'equipo'.
              Retorna None si ocurre algún error durante el proceso.
    """
    try:
        # Abrir la URL y crear un objeto BeautifulSoup
        f = urllib.request.urlopen(url, timeout=10)  # Añade un timeout de 10 segundos
        soup = BeautifulSoup(f, "lxml")

        award_data = []
        # Localizar el contenedor principal del artículo
        article_content = soup.find('div', class_='ArticleContent_article__NBhQ8')

        if article_content:
            # Iterar sobre los párrafos <p> dentro del article_content
            for p in article_content.find_all('p'):
                text = p.text.strip()
                # Buscar patrones como "2023-24 — Nikola Jokic, Denver Nuggets"
                match = re.match(r'(\d{4}-\d{2})\s*—\s*([^,]+),\s*([^\(]+)', text)  # Usa expresiones regulares
                if match:
                    year = match.group(1)  # Extrae el año (ej. "2023-24")
                    player = match.group(2).strip()  # Extrae el jugador
                    team = match.group(3).strip()  # Extrae el equipo
                    award_data.append({'year': year, 'player': player, 'team': team, 'award': award_name})
        return award_data

    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            print("Error de resolución de DNS: No se pudo encontrar el servidor.")
            return None
        else:
            print(f"Error al abrir la URL: {e}")
            return None
    except socket.timeout:
        print("Timeout al abrir la URL")
        return None
    except lxml.etree.XMLSyntaxError as e:
        print(f"Error al parsear el HTML: {e}")
        return None
    except Exception as e:  # Captura cualquier otra excepción
        print(f"Ocurrió un error inesperado: {e}")
        return None


def aggregate_player_awards(award_lists):
    """
    Agrega los premios ganados por cada jugador desde una lista de listas de premios.

    Args:
        award_lists (list): Una lista de listas, donde cada sublista contiene diccionarios representando premios.

    Returns:
        dict: Un diccionario donde las claves son los nombres de los jugadores y los valores son diccionarios
              con el conteo de cada tipo de premio que han ganado.
    """
    global player_award_counts  # Indica que estamos usando la variable global
    player_awards = {}
    for award_list in award_lists:
        for winner in award_list:
            player = winner['player']
            award = winner['award']
            if player not in player_awards:
                player_awards[player] = {}
            if award not in player_awards[player]:
                player_awards[player][award] = 0
            player_awards[player][award] += 1
    player_award_counts = player_awards
    return player_awards


if __name__ == "__main__":
    main_awards_url = "https://www.nba.com/news/history-all-time-awards"
    specific_awards_to_scrape = [
        "Regular season MVP",  # El nombre exacto como aparece en la página
        "Rookie of the Year",
        "Defensive Player of the Year",
        "Sixth Man of the Year",
        "Most Improved Player",
    ]

    extracted_award_urls = scrape_award_urls_from_strong_tags(main_awards_url, specific_awards_to_scrape)

    if extracted_award_urls:
        print("URLs de premios encontradas en la página principal:")
        for award, url in extracted_award_urls.items():
            print(f"URL {award}: {url}")

        all_awards = []
        for award, url in extracted_award_urls.items():  # Usa las URLs extraídas y almacenadas
            # Corregir la URL duplicada y reconstruir la URL completa
            url = url.replace("https://www.nba.com", "")
            full_url = f"https://www.nba.com{url}"
            awards = scrape_award_winners(full_url, award)
            if awards:
                all_awards.append(awards)

        player_awards = aggregate_player_awards(all_awards)

        print("\nPremios por Jugador (Formato Solicitado):")  # Formato de salida solicitado
        print(player_awards)

        # Imprime la variable global para verificar
        print("\nVariable Global:")
        print("player_award_counts:", player_award_counts)
        #print("award_urls:", award_urls)  # Imprime las URLs extraídas
    else:
        print("No se pudieron obtener las URLs de los premios desde la página principal.")