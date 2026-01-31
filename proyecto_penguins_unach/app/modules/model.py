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