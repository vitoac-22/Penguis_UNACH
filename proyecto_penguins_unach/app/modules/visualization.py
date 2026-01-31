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