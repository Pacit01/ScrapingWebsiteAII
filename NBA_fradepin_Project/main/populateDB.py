# encoding:utf-8  # Si es necesario para caracteres especiales

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NBA_fradepin_Project.settings')
django.setup()

from main.nba.models import Jugador, Estadistica, Premio
from Scraping_insideHoops_web import scrape_nba_leaders_dynamic_filtered
from Scraping_NBA_WEB import scrape_award_urls_from_strong_tags, scrape_award_winners, aggregate_player_awards
from datetime import datetime  # Aunque no se usa explícitamente, puede ser útil para fechas


# Función auxiliar que hace scraping en la web y carga los datos en la base de datos
def populateDB():

    # borramos todas las tablas de la BD
    Estadistica.objects.all().delete()
    Premio.objects.all().delete()
    Jugador.objects.all().delete()

    # 1. Extracción de Datos de Estadísticas
    url_stats = "http://www.insidehoops.com/nba_alltime_stats.shtml"
    leaders_data = scrape_nba_leaders_dynamic_filtered(url_stats)

    # 2. Extracción de Datos de Premios
    main_awards_url = "https://www.nba.com/news/history-all-time-awards"
    specific_awards_to_scrape = [
        "Regular season MVP",
        "Rookie of the Year",
        "Defensive Player of the Year",
        "Sixth Man of the Year",
        "Most Improved Player",
    ]
    extracted_award_urls = scrape_award_urls_from_strong_tags(main_awards_url, specific_awards_to_scrape)
    all_awards = []
    for award, url in extracted_award_urls.items():
        url = url.replace("https://www.nba.com", "")
        full_url = f"https://www.nba.com{url}"
        awards = scrape_award_winners(full_url, award)
        if awards:
            all_awards.append(awards)
    player_awards = aggregate_player_awards(all_awards)

    # 3. Almacenamiento en la Base de Datos

    # 3.1 Estadísticas
    if leaders_data:
        for player_data in leaders_data:
            try:
                jugador, created = Jugador.objects.get_or_create(nombre=player_data['Jugador'], equipo="Unknown")

                # Almacenamos en la BD
                estadistica = Estadistica.objects.create(
                    jugador=jugador,
                    puntos=player_data.get('PTS'),
                    rebotes=player_data.get('REB'),
                    asistencias=player_data.get('AST'),
                    robos=player_data.get('STL'),
                    tapones=player_data.get('BLK'),
                )

                # Imprimir datos extraídos (similar a tu estructura)
                print("Jugador:", player_data['Jugador'])
                print("Puntos:", player_data.get('PTS', "N/A"))
                print("Rebotes:", player_data.get('REB', "N/A"))
                print("Asistencias:", player_data.get('AST', "N/A"))
                print("Robos:", player_data.get('STL', "N/A"))
                print("Tapones:", player_data.get('BLK', "N/A"))
                print("-" * 20)

            except Exception as e:
                print(f"Error al procesar estadísticas de {player_data.get('Jugador')}: {e}")

    # 3.2 Premios
    if player_awards:
        for player, awards in player_awards.items():
            try:
                jugador, created = Jugador.objects.get_or_create(nombre=player, equipo="Unknown")
                for award_name, count in awards.items():
                    # Buscar todos los años en que el jugador ganó este premio
                    años_premio = []
                    for award_list in all_awards:
                        for winner in award_list:
                            if winner['player'] == player and winner['award'] == award_name:
                                años_premio.append(winner['year'])

                    # Crear premio solo si no existe
                    for año in años_premio:
                        premio, created = Premio.objects.get_or_create(
                            jugador=jugador,
                            nombre_premio=award_name,
                            año=año
                        )
                        
                        if created:
                            print(f"Nuevo premio creado - Jugador: {player}")
                            print(f"Premio: {award_name}")
                            print(f"Año: {año}")
                            print("-" * 20)

            except Exception as e:
                print(f"Error al procesar premios de {player}: {e}")

    return (Jugador.objects.count(), Estadistica.objects.count(), Premio.objects.count())


if __name__ == "__main__":
    conteo = populateDB()
    print("Conteo Final:")
    print(f"Jugadores: {conteo[0]}, Estadísticas: {conteo[1]}, Premios: {conteo[2]}")