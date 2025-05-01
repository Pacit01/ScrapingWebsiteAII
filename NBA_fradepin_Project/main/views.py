# encoding:utf-8
from django.shortcuts import render, redirect, get_object_or_404
# --- CORRECCIÓN 1: Importación de Modelos ---
# from main.nba.models import Jugador, Estadistica, Premio # Ruta incorrecta en tu estructura
from main.nba.models import Jugador, Estadistica, Premio # Importación relativa correcta

# --- CORRECCIÓN 2: Importación de Formularios ---
# from main.nba.forms import BusquedaJugadorForm, BusquedaPorPremioForm # Ruta incorrecta
from main.nba.forms import BusquedaJugadorForm, BusquedaPorPremioForm # Importa desde main/forms.py

# Los formularios de Login/Registro se importarán en sus vistas específicas si los usas
# from .forms.LoginForm import UserLoginForm # Ejemplo si estuvieran en main/forms/
# from .forms.RegisterForm import UserRegistrationForm # Ejemplo si estuvieran en main/forms/

from .populateDB import populateDB # Importa desde el mismo directorio de la app 'main'
from django.db.models import Q
from django.conf import settings
import os

# Configuración de Whoosh
INDEX_DIR = os.path.join(settings.BASE_DIR, 'indexdir')
WHOOSH_ENABLED = os.path.exists(INDEX_DIR)

if WHOOSH_ENABLED:
    try:
        from whoosh.index import open_dir
        from whoosh.qparser import QueryParser, MultifieldParser
        from whoosh import scoring
    except ImportError:
        WHOOSH_ENABLED = False
        print("Advertencia: Whoosh no está instalado. La búsqueda Whoosh estará deshabilitada.")

# Vista para cargar datos desde la web
def carga(request):
    if request.method == 'POST':
        if 'Aceptar' in request.POST:
            try:
                num_jugadores, num_estadisticas, num_premios = populateDB()
                mensaje = f"Se han almacenado: {num_jugadores} jugadores, {num_estadisticas} estadísticas, {num_premios} premios."
                if WHOOSH_ENABLED:
                    try:
                        populateDB()
                        from .whoosh_index import rebuild_index
                        print("Reconstruyendo índice Whoosh después de la carga...")
                        rebuild_index()
                        mensaje += " Índice Whoosh reconstruido."
                        print("Índice Whoosh reconstruido.")
                    except Exception as e:
                        mensaje += f" Error al reconstruir índice Whoosh: {e}"
                        print(f"Error al reconstruir índice Whoosh: {e}")
            except Exception as e:
                mensaje = f"Error durante la carga de datos: {e}"
                print(f"Error durante la carga de datos: {e}")
            # Usamos la ruta directa, sin el prefijo 'main/'
            return render(request, 'cargaBD.html', {'mensaje': mensaje})
        else:
            return redirect('main:inicio')
    return render(request, 'confirmacion.html')  # Sin prefijo 'main/'

def inicio(request):
    num_jugadores = Jugador.objects.count()
    # Utilizamos la plantilla 'inicio.html' que debe estar en main/templates/
    return render(request, 'inicio.html', {'num_jugadores': num_jugadores})


# Vista para listar todos los jugadores
def lista_jugadores(request):
    jugadores = Jugador.objects.all().order_by('nombre')
    # --- CORRECCIÓN 3: Ruta de Plantilla ---
    # ¡AÚN NECESITAS CREAR ESTA PLANTILLA: lista_jugadores.html!
    # return render(request, 'main/lista_jugadores.html', {'jugadores': jugadores})
    return render(request, 'lista_jugadores.html', {'jugadores': jugadores})

# Vista para mostrar los detalles de un jugador específico
def detalle_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, pk=jugador_id)
    estadisticas = jugador.estadisticas.first()
    premios = jugador.premios.all().order_by('-año')
    # --- CORRECCIÓN 3: Ruta de Plantilla ---
    # ¡AÚN NECESITAS CREAR ESTA PLANTILLA: detalle_jugador.html!
    # return render(request, 'main/detalle_jugador.html', { ... })
    return render(request, 'detalle_jugador.html', {
    'jugador': jugador,
    'estadisticas': estadisticas,
    'premios': premios
})

# Vista para buscar jugadores usando Whoosh
def buscar_jugadores_whoosh(request):
    form = BusquedaJugadorForm()
    resultados = []
    query_string = ""
    mensaje_error = ""

    if not WHOOSH_ENABLED:
        mensaje_error = "El índice de búsqueda (Whoosh) no está disponible o no se ha creado." # Mensaje más claro

    if request.method == 'POST' and WHOOSH_ENABLED:
        form = BusquedaJugadorForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['q']
            if query_string:
                try:
                    ix = open_dir(INDEX_DIR)
                    with ix.searcher(weighting=scoring.BM25F()) as searcher:
                        # Asegúrate que los campos coinciden con tu whoosh_index.py
                        parser = MultifieldParser(["nombre_jugador", "equipo", "premios", "content"], schema=ix.schema)
                        query = parser.parse(query_string)
                        resultados_whoosh = searcher.search(query, limit=20)
                        resultados_list = []
                        for hit in resultados_whoosh:
                            resultados_list.append({
                                'id': hit['id'],
                                'nombre': hit.get('nombre_jugador', 'N/A'),
                                'equipo': hit.get('equipo', 'N/A'),
                                'score': hit.score,
                                'highlights': hit.highlights("content")
                            })
                        resultados = resultados_list
                except Exception as e:
                    mensaje_error = f"Error durante la búsqueda Whoosh: {e}"
            else:
                 mensaje_error = "Por favor, introduce un término de búsqueda."

    # --- CORRECCIÓN 3: Ruta de Plantilla ---
    # ¡AÚN NECESITAS CREAR ESTA PLANTILLA: buscar_jugadores_whoosh.html!
    # return render(request, 'main/buscar_jugadores_whoosh.html', { ... })
    return render(request, 'buscar_jugadores_whoosh.html', { # Sin 'main/'
        'form': form,
        'resultados': resultados,
        'query': query_string,
        'mensaje_error': mensaje_error,
        'whoosh_enabled': WHOOSH_ENABLED
    })

# Vista para buscar jugadores usando Django ORM
def buscar_jugadores_django(request):
    form = BusquedaJugadorForm()
    resultados = []
    query_string = ""

    if request.method == 'POST':
        form = BusquedaJugadorForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['q']
            if query_string:
                resultados = Jugador.objects.filter(
                    Q(nombre__icontains=query_string) |
                    Q(equipo__icontains=query_string) |
                    Q(premios__nombre_premio__icontains=query_string)
                ).distinct().order_by('nombre')
            else:
                pass

    # --- CORRECCIÓN 3: Ruta de Plantilla ---
    # ¡AÚN NECESITAS CREAR ESTA PLANTILLA: buscar_jugadores_django.html!
    # return render(request, 'main/buscar_jugadores_django.html', { ... })
    return render(request, 'buscar_jugadores_django.html', { # Sin 'main/'
        'form': form,
        'resultados': resultados,
        'query': query_string
    })

# Vista para buscar por Premio Específico
def buscar_por_premio(request):
    form = BusquedaPorPremioForm(request.POST or None)
    context = {'form': form}

    if request.method == 'POST' and form.is_valid():
        premio_seleccionado = form.cleaned_data['premio']
        # Usamos values() y distinct() en lugar de distinct ON
        resultados = Premio.objects.filter(
            nombre_premio=premio_seleccionado
        ).select_related('jugador').order_by('-año')
        
        context.update({
            'premio_seleccionado': premio_seleccionado,
            'resultados': resultados
        })

    return render(request, 'buscar_por_premio.html', context)