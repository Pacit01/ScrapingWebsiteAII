import requests
from bs4 import BeautifulSoup
import re

def scrape_nba_leaders_dynamic_filtered(url):
    """
    Extrae los líderes históricos de la NBA de la página de InsideHoops y
    los organiza en una lista de diccionarios, incluyendo solo las categorías
    para las que el jugador tiene datos, y excluyendo la línea
    "*Active players are in CAPS.*".

    Args:
        url (str): La URL de la página con las estadísticas.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa a un jugador
              y sus estadísticas. Retorna None si hay un error.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        all_players_data = []
        pre_tag = soup.find('pre')

        if pre_tag:
            data = pre_tag.text.strip()
            stat_blocks = data.split('NBA ALL-TIME')
            stat_blocks = [block.strip() for block in stat_blocks if block.strip()]

            for block in stat_blocks:
                category_line = block.split('\n')[0]
                category_match = re.search(r'\((.*?)\)', category_line)
                if category_match:
                    category = category_match.group(1)
                else:
                    continue

                player_data = block.split('\n')[1:]
                for line in player_data:
                    if "*Active players are in CAPS." in line:  # Saltar esta línea
                        continue
                    parts = line.split()
                    if len(parts) > 1:
                        stat_value = parts[-1]
                        player = ' '.join(parts[:-1]).strip()

                        # Buscar si ya existe el jugador en la lista
                        player_entry = next((item for item in all_players_data if item["Jugador"] == player), None)

                        if player_entry:
                            # Si el jugador ya existe, actualizar la estadística correspondiente
                            player_entry[category] = int(stat_value.replace(',', '')) if stat_value.isdigit() else stat_value
                        else:
                            # Si el jugador no existe, crear una nueva entrada con SOLO la categoría actual
                            new_player_entry = {
                                "Jugador": player,
                                category: int(stat_value.replace(',', '')) if stat_value.isdigit() else stat_value
                            }
                            all_players_data.append(new_player_entry)

        else:
            print("No se encontró la etiqueta <pre> con los datos.")
            return None

        return all_players_data

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return None
    except Exception as e:
        print(f"Error al procesar la página: {e}")
        return None


if __name__ == "__main__":
    url = "http://www.insidehoops.com/nba_alltime_stats.shtml"
    leaders = scrape_nba_leaders_dynamic_filtered(url)

    if leaders:
        print("Líderes Históricos de la NBA (Dinámico, Filtrado):")
        for player in leaders:
            print(player)
    else:
        print("No se pudieron obtener los datos de los líderes.")