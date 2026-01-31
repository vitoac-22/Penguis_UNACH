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