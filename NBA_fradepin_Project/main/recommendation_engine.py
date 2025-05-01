# main/recommendation_engine.py

# Este archivo está destinado a contener la lógica para el motor de recomendación de jugadores.
# Actualmente no está implementado.

# Posibles ideas futuras:
# - Encontrar jugadores con estadísticas similares a uno dado.
# - Recomendar jugadores basados en patrones de premios.
# - Sugerir jugadores para un "equipo de fantasía" simple basado en criterios.

# ---------------------------------------------------------------------------
# EJEMPLO PLACEHOLDER - NO FUNCIONAL SIN IMPLEMENTACIÓN DETALLADA
# ---------------------------------------------------------------------------

def get_player_recommendations(player_id, num_recommendations=5):
    """
    Función placeholder para obtener recomendaciones de jugadores.
    (Actualmente no implementada - Devuelve una lista vacía)

    Args:
        player_id (int): El ID del jugador para el que se buscan recomendaciones.
        num_recommendations (int): El número de recomendaciones a devolver.

    Returns:
        list: Una lista vacía, ya que la lógica no está implementada.
    """
    # --- INICIO DE LA LÓGICA DE RECOMENDACIÓN (POR IMPLEMENTAR) ---

    # Paso 1: Obtener datos del jugador base (ej. sus estadísticas, premios)
    # try:
    #     from .models import Jugador, Estadistica, Premio
    #     jugador_base = Jugador.objects.get(pk=player_id)
    #     # estadisticas_base = jugador_base.estadisticas.first()
    #     # premios_base = list(jugador_base.premios.values_list('nombre_premio', flat=True))
    # except Jugador.DoesNotExist:
    #      print(f"Error: Jugador con ID {player_id} no encontrado.")
    #      return []
    # except Exception as e:
    #      print(f"Error obteniendo datos del jugador base: {e}")
    #      return []

    # Paso 2: Definir la estrategia de recomendación
    #   - ¿Basada en similitud de estadísticas? (requiere normalización, cálculo de distancia/similitud)
    #   - ¿Basada en premios compartidos?
    #   - ¿Combinación?
    #   - ¿Filtrar por posición, equipo, época? (requeriría más datos)

    # Paso 3: Obtener datos de otros jugadores (candidatos)
    #   candidatos = Jugador.objects.exclude(pk=player_id)
    #   # Podrías necesitar pre-cargar estadísticas o premios para eficiencia:
    #   # candidatos = candidatos.prefetch_related('estadisticas', 'premios')

    # Paso 4: Calcular la "puntuación" de recomendación para cada candidato
    #   puntuaciones = {}
    #   for candidato in candidatos:
    #       # Calcular similitud basada en la estrategia definida
    #       # score = calcular_similitud(jugador_base, candidato)
    #       # puntuaciones[candidato] = score
    #       pass # Placeholder

    # Paso 5: Ordenar candidatos por puntuación y seleccionar los mejores N
    #   jugadores_ordenados = sorted(puntuaciones, key=puntuaciones.get, reverse=True)
    #   recomendaciones_finales = jugadores_ordenados[:num_recommendations]

    # --- FIN DE LA LÓGICA DE RECOMENDACIÓN (POR IMPLEMENTAR) ---

    # Por ahora, simplemente imprimimos una advertencia y devolvemos una lista vacía.
    print(f"ADVERTENCIA: La función de recomendación para el jugador ID {player_id} no está implementada.")
    recomendaciones_finales = [] # Devuelve lista vacía

    return recomendaciones_finales


# ---------------------------------------------------------------------------
# Ejemplo MUY BÁSICO y conceptual de similitud por estadísticas (NO USAR DIRECTAMENTE)
# Necesita librerías como numpy y scikit-learn (`pip install numpy scikit-learn`)
# y una implementación mucho más robusta.
# ---------------------------------------------------------------------------
# from .models import Jugador, Estadistica
# import numpy as np
# from sklearn.preprocessing import StandardScaler # Para normalizar
# from sklearn.metrics.pairwise import cosine_similarity # Para calcular similitud
#
# def get_similar_players_by_stats_conceptual(player_id, num_recommendations=5):
#     """Ejemplo conceptual de búsqueda de similitud por estadísticas."""
#     try:
#         target_stat = Estadistica.objects.filter(jugador_id=player_id).first()
#         if not target_stat:
#             print(f"No hay estadísticas para el jugador {player_id}")
#             return []
#
#         # Obtenemos estadísticas de otros jugadores (excluyendo al jugador base)
#         all_other_stats = Estadistica.objects.exclude(jugador_id=player_id).select_related('jugador')
#         if not all_other_stats:
#             print("No hay estadísticas de otros jugadores para comparar.")
#             return []
#
#         # Crear vectores numéricos (usando 0 si falta algún dato)
#         target_vector = np.array([[
#             target_stat.puntos or 0, target_stat.rebotes or 0, target_stat.asistencias or 0,
#             target_stat.robos or 0, target_stat.tapones or 0
#         ]])
#         other_vectors_list = []
#         players_map = [] # Para mapear el índice del vector al objeto Jugador
#         for s in all_other_stats:
#             other_vectors_list.append([
#                 s.puntos or 0, s.rebotes or 0, s.asistencias or 0,
#                 s.robos or 0, s.tapones or 0
#             ])
#             players_map.append(s.jugador)
#         other_vectors = np.array(other_vectors_list)
#
#         # --- Normalización (¡Esencial!) ---
#         # Combinamos todos los vectores para escalar conjuntamente
#         all_vectors = np.vstack((target_vector, other_vectors))
#         scaler = StandardScaler()
#         # Escalamos los datos (media 0, desviación estándar 1)
#         scaled_vectors = scaler.fit_transform(all_vectors)
#         target_norm = scaled_vectors[0:1] # Vector normalizado del jugador base
#         other_norm = scaled_vectors[1:]   # Vectores normalizados de los otros
#
#         # --- Cálculo de Similitud ---
#         # Usamos similitud de coseno entre el jugador base y todos los demás
#         similarities = cosine_similarity(target_norm, other_norm)[0] # Obtenemos un array de similitudes
#
#         # --- Selección de los Mejores ---
#         # Obtenemos los índices de los jugadores ordenados por similitud (de mayor a menor)
#         similar_indices = np.argsort(similarities)[::-1]
#
#         # Construimos la lista de jugadores recomendados
#         recommended_players = []
#         for i in similar_indices[:num_recommendations]:
#             # Podrías añadir un umbral mínimo de similitud si quieres
#             # if similarities[i] > 0.5:
#             recommended_players.append(players_map[i]) # Añadimos el objeto Jugador correspondiente
#
#         return recommended_players
#
#     except Estadistica.DoesNotExist:
#         # Esto no debería ocurrir por el filter().first() pero por si acaso
#         print(f"Error interno: No se encontraron estadísticas para {player_id}")
#         return []
#     except Exception as e:
#         # Captura otros posibles errores (ej. de numpy/sklearn)
#         print(f"Error calculando similitud por estadísticas: {e}")
#         return []