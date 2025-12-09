# main.py
import threading
import time
import logging
from sistema_atencion import SistemaAtencion
from taxi import Taxi
from cliente import Cliente

# Duración total de la simulación en segundos
DURACION_SIMULACION = 12

def inicializar_datos():
    """Define los datos iniciales de taxis y clientes."""
    
    # Lista de Taxis: ID, Marca, Placa, Ubicación Inicial (x, y)
    datos_taxis = [
        ("T1", "Toyota", "ABC123", (5, 5)),
        ("T2", "Nissan", "DEF456", (1, 9)),
        ("T3", "Ford", "GHI789", (10, 1)),
    ]

    # Lista de Clientes: Nombre, Origen (x, y), Destino (x, y)
    datos_clientes = [
        ("Maria", (2, 4), (8, 1)),
        ("Juan", (11, 8), (4, 12)),
        ("Pepe", (6, 6), (2, 9)),
        ("Ana", (1, 1), (10, 10)),
        ("Luis", (15, 3), (7, 7)),
    ]
    
    return datos_taxis, datos_clientes

def main():
    """Función principal para configurar y ejecutar la simulación."""
    logging.info("--- INICIO DE LA SIMULACIÓN UNIETAXI ---")

    # Inicializar el Sistema de Atención (El recurso compartido)
    sistema_central = SistemaAtencion()
    
    # Obtener datos
    datos_taxis, datos_clientes = inicializar_datos()
    
    # Crear y lanzar los Hilos Taxi
    hilos_taxis = []
    for id_vehiculo, marca, placa, ubicacion in datos_taxis:
        taxi = Taxi(id_vehiculo, marca, placa, ubicacion, sistema_central, DURACION_SIMULACION)
        hilos_taxis.append(taxi)
        taxi.start()

    # Crear y lanzar los Hilos Cliente
    hilos_clientes = []
    for nombre, origen, destino in datos_clientes:
        cliente = Cliente(nombre, origen, destino, sistema_central)
        hilos_clientes.append(cliente)
        cliente.start()
    
    logging.info(f"Simulación ejecutándose por {DURACION_SIMULACION} segundos...")
    
    # Esperar la duración de la simulación
    time.sleep(DURACION_SIMULACION)
    
    # Detener Taxis
    for taxi in hilos_taxis:
        taxi.ejecutando.clear() # Señal de parada
    
    # Esperar a que todos los hilos terminen (Join)
    for taxi in hilos_taxis:
        taxi.join()
    for cliente in hilos_clientes:
        cliente.join()

    # --- RESULTADOS FINALES ---
    print("\n" + "="*50)
    print("      *** REPORTE DE CIERRE DE JORNADA ***")
    print("="*50)
    
    # Mostrar la ganancia final de cada taxi
    for taxi in hilos_taxis:
        print(f"💰 {taxi.name} ({taxi.marca}, {taxi.placa}): Ganancia Total: {taxi.ganancia_total} Euros")
    
    print("="*50 + "\n")
    logging.info("--- SIMULACIÓN FINALIZADA ---")

if __name__ == "__main__":
    # Configurar el logging en el main también para controlar el formato
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')
    main()