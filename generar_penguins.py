import os

# Nombre de la carpeta raíz (sin caracteres raros para que tu terminal no llore)
PROJECT_NAME = "proyecto_penguins_unach"

# --- CONTENIDO DE LOS ARCHIVOS ---
# Aquí definimos qué lleva cada archivo. Todo está actualizado a la versión "Penguins"
# que discutimos: limpieza de outliers, Random Forest y Plotly con descarga PNG.

file_contents = {}

# 1. REQUIREMENTS
file_contents[f"{PROJECT_NAME}/requirements.txt"] = """flask
pandas
numpy
scikit-learn
plotly
"""

# 2. EXCEPCIONES (Personalizada)
file_contents[f"{PROJECT_NAME}/app/modules/exceptions.py"] = """
class ErrorDeDatos(Exception):
    \"\"\"Clase base.\"\"\"
    pass

class DataInvalidaError(ErrorDeDatos):
    \"\"\"
    Excepción personalizada para cuando el dataset de pingüinos
    no cumple con la estructura o calidad mínima.
    \"\"\"
    def __init__(self, mensaje="El archivo CSV no es válido para este análisis."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)
"""

# 3. PREPROCESAMIENTO (Limpieza + Outliers)
file_contents[f"{PROJECT_NAME}/app/modules/preprocessing.py"] = """
import pandas as pd
import numpy as np
from .exceptions import DataInvalidaError

def cargar_y_limpiar(file_stream):
    try:
        # Carga
        df = pd.read_csv(file_stream)
        
        # Validación de columnas críticas
        cols_requeridas = ['species', 'bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
        if not set(cols_requeridas).issubset(df.columns):
            raise DataInvalidaError("Faltan columnas críticas del dataset de Pingüinos.")

        # 1. Manejo de Nulos (Eliminación directa para asegurar calidad)
        df_clean = df.dropna().copy()

        # 2. Eliminación de Outliers (Rango Intercuartílico) - Requisito explícito
        # Filtramos pingüinos con medidas físicas absurdas
        for col in ['bill_length_mm', 'body_mass_g']:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]

        if df_clean.empty:
            raise DataInvalidaError("La limpieza eliminó todos los datos. Revisa el CSV.")

        return df_clean

    except Exception as e:
        if isinstance(e, DataInvalidaError):
            raise e
        raise DataInvalidaError(f"Error en preprocesamiento: {str(e)}")
"""

# 4. MODELO (Random Forest + Simulación de Predicción)
file_contents[f"{PROJECT_NAME}/app/modules/model.py"] = """
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def entrenar_predecir(df):
    # Features y Target
    X = df[['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']]
    y = df['species']

    # Split: Usamos X_test como si fueran "nuevos datos" subidos por el usuario
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Entrenamiento
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Predicción (Simulando nuevos datos)
    y_pred = clf.predict(X_test)
    
    # Métricas
    acc = accuracy_score(y_test, y_pred)
    
    # Preparamos dataframe de resultados para mostrar
    resultados = X_test.copy()
    resultados['Especie_Real'] = y_test
    resultados['Prediccion_Modelo'] = y_pred
    
    return acc, resultados
"""

# 5. VISUALIZACIÓN (Plotly + Config PNG)
file_contents[f"{PROJECT_NAME}/app/modules/visualization.py"] = """
import plotly.express as px
import plotly.utils
import json

def crear_graficos(df_resultados):
    # Gráfico: Dispersión Real vs Predicción
    fig = px.scatter(
        df_resultados, 
        x='body_mass_g', 
        y='flipper_length_mm',
        color='Prediccion_Modelo', 
        symbol='Especie_Real',
        title='Clasificación de Pingüinos: Real (Forma) vs Predicción (Color)',
        labels={'body_mass_g': 'Masa Corporal (g)', 'flipper_length_mm': 'Aleta (mm)'},
        template='plotly_dark'
    )
    
    # Configuración para habilitar descarga PNG explícita
    config = {
        'toImageButtonOptions': {
            'format': 'png', 
            'filename': 'prediccion_pinguinos',
            'height': 500,
            'width': 700,
            'scale': 1 
        }
    }
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder), config
"""

# 6. APP INIT
file_contents[f"{PROJECT_NAME}/app/__init__.py"] = """
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'clave_super_secreta_unach' 
    
    from .routes import main
    app.register_blueprint(main)
    
    return app
"""

# 7. ROUTES (Controlador Principal con Try-Except-Finally)
file_contents[f"{PROJECT_NAME}/app/routes.py"] = """
from flask import Blueprint, render_template, request, flash, redirect
from .modules.preprocessing import cargar_y_limpiar
from .modules.model import entrenar_predecir
from .modules.visualization import crear_graficos
from .modules.exceptions import DataInvalidaError

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        
        try: # Inicio del bloque de manejo de errores
            if not file or file.filename == '':
                raise DataInvalidaError("No se seleccionó ningún archivo.")

            # 1. Preprocesamiento
            df_clean = cargar_y_limpiar(file)
            
            # 2. ML y Predicción
            accuracy, df_resultados = entrenar_predecir(df_clean)
            
            # 3. Visualización
            graphJSON, config = crear_graficos(df_resultados)
            
            msg = f"Entrenamiento completado. Precisión del modelo: {accuracy:.2%}"
            
            return render_template(
                'dashboard.html', 
                graphJSON=graphJSON, 
                config=config,
                message=msg,
                tables=[df_resultados.head(5).to_html(classes='table table-dark', index=False)]
            )

        except DataInvalidaError as e:
            flash(f"Error de Datos: {e.mensaje}", 'danger')
            return redirect(request.url)
            
        except Exception as e:
            flash(f"Error Inesperado: {str(e)}", 'warning')
            return redirect(request.url)
            
        finally:
            print("--- Ciclo de procesamiento finalizado ---")

    return render_template('index.html')
"""

# 8. TEMPLATES
file_contents[f"{PROJECT_NAME}/app/templates/index.html"] = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>UNACH - Pingüinos ML</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-white d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card bg-secondary text-white p-4" style="width: 400px;">
        <h3 class="text-center mb-4">Clasificador de Pingüinos</h3>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <form method="POST" enctype="multipart/form-data">
            <div class="mb-3">
                <label class="form-label">Subir dataset (penguins.csv)</label>
                <input type="file" name="file" class="form-control" accept=".csv" required>
            </div>
            <button type="submit" class="btn btn-info w-100">Procesar Modelo</button>
        </form>
    </div>
</body>
</html>
"""

file_contents[f"{PROJECT_NAME}/app/templates/dashboard.html"] = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>Resultados ML</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body class="bg-dark text-white">
    <div class="container mt-4">
        <h2 class="border-bottom pb-2">Resultados del Análisis</h2>
        <div class="alert alert-success mt-3">{{ message }}</div>
        
        <div class="card bg-secondary mb-4">
            <div class="card-body">
                <div id="chart"></div>
            </div>
            <div class="card-footer text-muted">
                <small>Nota: Usa la cámara en la barra del gráfico para descargar PNG</small>
            </div>
        </div>

        <h4>Muestra de Predicciones (Test Set)</h4>
        <div class="table-responsive">
            {{ tables[0]|safe }}
        </div>
        
        <a href="/" class="btn btn-outline-light mt-4 mb-5">Volver a intentar</a>
    </div>

    <script type="text/javascript">
        var graphs = {{ graphJSON | safe }};
        var config = {{ config | safe }};
        Plotly.newPlot('chart', graphs, {}, config);
    </script>
</body>
</html>
"""

# 9. RUN.PY
file_contents[f"{PROJECT_NAME}/run.py"] = """
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

# 10. README
file_contents[f"{PROJECT_NAME}/README.md"] = """
# Proyecto Pingüinos UNACH - Programación Modular

Este proyecto cumple los requerimientos de la Actividad Autónoma 7, Unidad 4.

## Estructura
- **app/modules/**: Contiene lógica separada para Preprocesamiento, ML y Visualización.
- **app/modules/exceptions.py**: Excepción `DataInvalidaError`.
- **Preprocesamiento**: Limpia nulos y elimina outliers (IQR).
- **ML**: RandomForestClassifier.
- **Visualización**: Plotly interactivo con descarga PNG.

## Ejecución
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar: `python run.py`
3. Subir el archivo `penguins 2.csv`.
"""

# --- LÓGICA DE GENERACIÓN ---
def create_file_structure():
    print(f"Iniciando construcción de {PROJECT_NAME}...")
    
    for filepath, content in file_contents.items():
        # Crear directorios si no existen
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Carpeta creada: {directory}")
            
        # Escribir archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Archivo generado: {filepath}")

    print("\\n¡Estructura generada con éxito! Ahora ejecuta:")
    print(f"cd {PROJECT_NAME}")
    print("pip install -r requirements.txt")
    print("python run.py")

if __name__ == "__main__":
    create_file_structure()