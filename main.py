# main.py
import threading
import time
import logging
import random
from datetime import datetime, timedelta
from sistema_atencion import SistemaAtencion
from taxi import Taxi
from cliente import Cliente

# Configuración de la simulación
HORA_INICIO = datetime.strptime('10:00:00', '%H:%M:%S')
HORA_FIN = datetime.strptime('00:00:00', '%H:%M:%S') + timedelta(days=1) # Medianoche

# La duración de la simulación real será de 15 segundos para dar tiempo a la recogida inicial
DURACION_REAL_SIMULACION = 15

def inicializar_datos():
    """Define los datos iniciales de 5 taxis y 9 clientes."""
    
    # 5 Taxis: ID, Marca, Placa, Ubicación Inicial (x, y)
    datos_taxis = [
        ("TAXI 1", "Toyota", "ABC123", (5, 5)),
        ("TAXI 2", "Nissan", "DEF456", (1, 9)),
        ("TAXI 3", "Ford", "GHI789", (10, 1)),
        ("TAXI 4", "BMW", "JKL012", (15, 15)),
        ("TAXI 5", "Audi", "MNO345", (7, 12)),
    ]

    # 9 Clientes: Nombre, Origen (x, y), Destino (x, y)
    datos_clientes = [
        ("Maria G.", (2, 4), (8, 1)),
        ("Juan P.", (11, 8), (4, 12)),
        ("Pepe L.", (6, 6), (2, 9)),
        ("Ana S.", (1, 1), (10, 10)),
        ("Luis M.", (15, 3), (7, 7)),
        ("Elena C.", (18, 1), (5, 14)),
        ("Carlos F.", (3, 16), (11, 2)),
        ("Sofia T.", (9, 11), (1, 1)),
        ("David H.", (14, 10), (3, 6)),
    ]
    
    return datos_taxis, datos_clientes

def main():
    """Función principal para configurar y ejecutar la simulación."""
    
    # Usar un formato de log más limpio
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("\n" + "="*80)
    print("      *** INICIO DE LA SIMULACIÓN UNIETAXI - JORNADA 10:00:00 a 00:00:00 ***")
    print("="*80)

    # Inicializar el Sistema de Atención y el Reloj
    sistema_central = SistemaAtencion(HORA_INICIO, HORA_FIN)
    
    # Evento para controlar la ejecución del bucle de los Taxis (el reloj)
    reloj_running = threading.Event()
    reloj_running.set() 
    
    # Obtener datos
    datos_taxis, datos_clientes = inicializar_datos()
    
    # Crear y lanzar los Hilos Taxi
    hilos_taxis = []
    for id_vehiculo, marca, placa, ubicacion in datos_taxis:
        taxi = Taxi(id_vehiculo, marca, placa, ubicacion, sistema_central, reloj_running)
        hilos_taxis.append(taxi)
        taxi.start()

    # Crear y lanzar los Hilos Cliente
    hilos_clientes = []
    for nombre, origen, destino in datos_clientes:
        cliente = Cliente(nombre, origen, destino, sistema_central)
        hilos_clientes.append(cliente)
        # Inicialmente, solo una parte de los clientes "pide" servicio
        if random.random() < 0.7:
             cliente.start()
        else:
             hilos_clientes.remove(cliente) # No se usa este cliente
    
    
    # --- Bucle de ejecución de la simulación ---
    
    tiempo_inicio_real = time.time()
    
    while sistema_central.get_tiempo_simulado() < HORA_FIN and (time.time() - tiempo_inicio_real) < DURACION_REAL_SIMULACION:
        # Esto permite que el main sea el controlador del tiempo y evita que se quede esperando
        time.sleep(0.5) 

    
    # -------------------------------------------
    
    # Detener Taxis forzadamente al llegar a medianoche (simulada) o al límite real
    reloj_running.clear() 
    
    # Esperar a que todos los hilos terminen
    for taxi in hilos_taxis:
        taxi.join()
    for cliente in hilos_clientes:
        cliente.join()

    # --- REPORTE DE CIERRE DE JORNADA ---
    print("\n" + "="*80)
    print(f"      *** REPORTE FINAL DE JORNADA ({HORA_INICIO.strftime('%H:%M:%S')} - {HORA_FIN.strftime('%H:%M:%S')}) ***")
    print("="*80)
    
    # 1. Ganancias y Calificación
    print("\n--- 💰 GANANCIAS Y CALIFICACIONES DEL DÍA ---")
    for taxi in hilos_taxis:
        print(f"✅ {taxi.name} ({taxi.marca, taxi.placa}):")
        print(f"   - Ganancia Total Registrada: {taxi.ganancia_total} Euros.")
        print(f"   - Viajes Registrados: {taxi.num_viajes}.")
        print(f"   - Calificación Media (1-5): {taxi.calificacion_media} ⭐")

    # 2. Resumen de Viajes
    print("\n--- 📋 DETALLE DE VIAJES REGISTRADOS ---")
    if sistema_central.viajes_completados:
        for viaje in sistema_central.viajes_completados:
            print(f"   - {viaje['taxi_id']} recogió a {viaje['cliente_nombre']} a las {viaje['hora_recogida']} y lo dejó a las {viaje['hora_llegada']}. Costo: {viaje['costo']}€.")
    else:
        print("   (No se registraron viajes completados en este periodo.)")

    print("\n" + "="*80)
    print("      *** SIMULACIÓN FINALIZADA ***")
    print("="*80)

if __name__ == "__main__":
    # Configurar el logging en el main también para controlar el formato
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')
    main()