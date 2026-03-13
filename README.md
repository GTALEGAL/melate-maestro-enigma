# 🛰️ CONDOMINIO B - ENIGMA 2.0 (NASA EDITION)
**Terminal de Análisis Predictivo y Resonancia Numérica para Melate**

---

## 📖 DESCRIPCIÓN DEL PROYECTO
El **Condominio B** es una estación de control diseñada para procesar datos históricos de sorteos numéricos y extraer vectores de resonancia de alta probabilidad. Inspirado en las terminales de control de misión de la década de los 80, combina una estética retro con un motor analítico moderno en Python.

## 🛠️ ARQUITECTURA DEL SISTEMA
* **CORE:** Python 3.10 (Pandas/Numpy).
* **INTERFACE:** HTML5/CSS3 con diseño CRT e interactividad por comandos.
* **DEPLOYMENT:** Vercel Serverless Architecture.
* **DATABASE:** `datos.csv` (Registro histórico de sorteos).

## 🚀 FUNCIONALIDADES ACTUALES
- [x] **Input Dinámico:** Entrada de "Gatillos" numéricos desde la terminal principal.
- [x] **Análisis de 7 Puntos:** Generación de los 7 socios más frecuentes asociados a un número.
- [x] **Métricas NASA:**
    - **Balance de Paridad:** Ratio de números Pares/Nones.
    - **Media del Vector:** Promedio matemático de la jugada.
    - **Nivel de Confianza:** Cálculo de densidad de datos históricos.
- [x] **Interfaz Blindada:** Sistema de captura de comandos vía `form submit` para ejecución garantizada.

## 📋 COMANDOS DISPONIBLES
1.  **[Número]:** Ingresa cualquier número (1-56) para generar su vector de resonancia.
2.  **Enter:** Ejecuta la orden y despliega el reporte en pantalla.

## 🛰️ HOJA DE RUTA (PRÓXIMOS LANZAMIENTOS)
1.  **Módulo HISTORIAL:** Almacenamiento temporal de las últimas 5 trayectorias.
2.  **SIMULADOR DE VUELO (Backtesting):** Comparación del vector contra la historia para verificar efectividad.
3.  **ALERTA DORADA:** Notificación visual cuando los parámetros de paridad y media coincidan con patrones ganadores históricos.

---
**DIRECTOR DE MISIÓN:** [User]  
**ESTADO:** OPERATIVO // VIERNES 13 MARZO 2026
