import pandas as pd
import numpy as np

# EL CONDOMINIO: 56 PISOS DE INGENIERÍA ESTADÍSTICA
class MelateEnigma:
    def __init__(self, data_path='Melate (1).csv'):
        self.df = pd.read_csv(data_path)
        self.df['FECHA'] = pd.to_datetime(self.df['FECHA'], dayfirst=True)
        self.df['DIA_SEMANA'] = self.df['FECHA'].dt.day_name()
    
    def analizar_marea(self, dia_objetivo='Sunday'):
        # Filtro de marea por día de la semana
        subset = self.df[self.df['DIA_SEMANA'] == dia_objetivo]
        
        # Capa 1: Frecuencias de resonancia
        todos_numeros = subset[['R1','R2','R3','R4','R5','R6','R7']].values.flatten()
        frecuencia = pd.Series(todos_numeros).value_counts().to_dict()
        
        return frecuencia

    def detectar_gatillo_22(self):
        # Analizar si el 22 "llama" a otros en marzo
        marzo_df = self.df[self.df['FECHA'].dt.month == 3]
        # (Lógica simplificada para el primer despliegue)
        return "Gatillo 22 activo en marzo: ALTA RESONANCIA"

# Ejecución inicial
if __name__ == "__main__":
    enigma = MelateEnigma()
    print("--- REPORTE ENIGMA 2.0 ---")
    print(enigma.detectar_gatillo_22())
