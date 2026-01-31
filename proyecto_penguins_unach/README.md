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