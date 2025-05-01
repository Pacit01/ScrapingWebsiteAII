    # encoding:utf-8
import os
import django

# 1. Configurar el entorno de Django
# Ajusta 'NBA_fradepin_Project.settings' si tu archivo de settings está en otro lugar
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NBA_fradepin_Project.settings')
django.setup()

# 2. Importar Whoosh y modelos Django DESPUÉS de django.setup()
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, ID, TEXT, KEYWORD # KEYWORD es útil para campos exactos
from whoosh.analysis import StemmingAnalyzer
from django.conf import settings # Para obtener BASE_DIR
from main.nba.models import Jugador # Importa tus modelos

# 3. Definir la ubicación del índice
# Usamos BASE_DIR para que la ruta sea relativa al proyecto
INDEX_DIR = os.path.join(settings.BASE_DIR, "indexdir")

# 4. Definir el Schema del Índice
# Qué campos queremos indexar y cómo
def get_schema():
    return Schema(
        # ID del Jugador (clave primaria de Django)
        # stored=True: guarda el valor en el índice para recuperarlo directamente
        # unique=True: asegura que cada ID de jugador es único en el índice
        id=ID(stored=True, unique=True),

        # Nombre del Jugador
        # TEXT: campo de texto completo, bueno para búsquedas flexibles
        # analyzer=StemmingAnalyzer(): reduce palabras a su raíz (ej. "running" -> "run")
        # stored=True: guarda el nombre para mostrar en resultados sin consultar la BD
        nombre_jugador=TEXT(stored=True, analyzer=StemmingAnalyzer()),

        # Equipo del Jugador
        # TEXT: Permite búsqueda parcial, también con Stemming
        # stored=True: Guarda el equipo
        equipo=TEXT(stored=True, analyzer=StemmingAnalyzer()),

        # Premios Ganados (como texto concatenado)
        # Se guardarán los nombres de los premios como un solo string separado por espacios
        premios=TEXT(analyzer=StemmingAnalyzer()),

        # Campo 'content' genérico (opcional pero útil)
        # Combina texto de varios campos para una búsqueda general
        content=TEXT(analyzer=StemmingAnalyzer())
    )

# 5. Función para (re)construir el índice
def rebuild_index():
    """
    Borra el índice existente (si lo hay) y lo reconstruye desde cero
    con los datos actuales de la base de datos Django.
    """
    print(f"Verificando directorio del índice en: {INDEX_DIR}")
    if not os.path.exists(INDEX_DIR):
        print("Creando directorio para el índice...")
        os.makedirs(INDEX_DIR)
    else:
        print("Directorio del índice ya existe.")

    print("Creando nuevo índice Whoosh...")
    ix = create_in(INDEX_DIR, get_schema()) # Crea (o sobrescribe) el índice

    print("Abriendo escritor del índice...")
    # Usamos 'with' para asegurar que el writer se cierre correctamente
    with ix.writer() as writer:
        print("Indexando jugadores desde la base de datos Django...")
        # Obtenemos todos los jugadores
        # prefetch_related es una optimización para cargar premios relacionados eficientemente
        jugadores = Jugador.objects.all().prefetch_related('premios')
        count = 0
        total = jugadores.count()

        for jugador in jugadores:
            # Construimos el string de premios para este jugador
            lista_premios = [p.nombre_premio for p in jugador.premios.all()]
            texto_premios = " ".join(lista_premios)

            # Creamos el contenido combinado para el campo 'content'
            contenido_combinado = f"{jugador.nombre} {jugador.equipo} {texto_premios}"

            # Añadimos el documento al índice
            try:
                writer.add_document(
                    id=str(jugador.pk), # Whoosh espera strings para ID a menudo
                    nombre_jugador=jugador.nombre,
                    equipo=jugador.equipo or "", # Asegura que no sea None
                    premios=texto_premios,
                    content=contenido_combinado
                )
                count += 1
                if count % 100 == 0: # Imprime progreso cada 100 jugadores
                    print(f"Indexados {count}/{total} jugadores...")
            except Exception as e:
                 print(f"Error indexando jugador {jugador.pk} ({jugador.nombre}): {e}")

        print(f"Indexación completada. Total jugadores procesados: {count}")
    print("Escritor del índice cerrado y cambios guardados.")

# 6. Permitir ejecutar el script directamente
if __name__ == "__main__":
    print("--- Iniciando Reconstrucción del Índice Whoosh ---")
    rebuild_index()
    print("--- Proceso de Reconstrucción Finalizado ---")