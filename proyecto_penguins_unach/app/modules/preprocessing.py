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