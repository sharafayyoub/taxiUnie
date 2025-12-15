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

# Duración real que la simulación debe correr (Aprox. 60 segundos para 14h simuladas)
DURACION_REAL_SIMULACION = 60 

# --- Hilo del Reloj ---
class RelojSistema(threading.Thread):
    """Hilo encargado de avanzar el tiempo simulado de forma continua."""
    def __init__(self, sistema_central, duracion_real):
        super().__init__(name="RelojSistema")
        self.sistema_central = sistema_central
        self.running = threading.Event()
        self.running.set()
        self.tiempo_inicio_real = time.time()
        self.duracion_real = duracion_real
        self.intervalo_avance = 0.5 # Avance el reloj cada 0.5 segundos reales

    def run(self):
        # El reloj sigue corriendo mientras el tiempo real no se agote Y no hayamos pasado la medianoche simulada
        while self.running.is_set() and (time.time() - self.tiempo_inicio_real < self.duracion_real):
            # Usamos el sistema central para avanzar el tiempo simulado
            if self.sistema_central.avanzar_tiempo(self.intervalo_avance):
                time.sleep(self.intervalo_avance)
            else:
                self.running.clear() # Detener si ha pasado la medianoche simulada

    def stop(self):
        self.running.clear()


def inicializar_datos():
    """Define los datos iniciales de 5 taxis y 9 clientes."""
    
    # 5 Taxis: ID, Marca, Placa, Ubicación Inicial (x, y)
    datos_taxis = [
        ("TAXI 1", "Toyota", "ABC123", (5, 5)),
        ("TAXI 2", "Nissan", "DEF456", (1, 9)),
        ("TAXI 3", "Ford", "GHI789", (10, 1)),
        ("TAXI 4", "BMW", "JKL012", (15, 15)),
        ("TAXI 5", "Audi", "MNO345", (7, 12)),
        ("TAXI 6", "Mercedez", "PQR678", (20, 2)),
        ("TAXI 7", "Honda", "STU901", (3, 18)),
        ("TAXI 8", "Volvo", "VWX234", (12, 12)),
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
        ("Raul V.", (1, 15), (10, 5)),
        ("Sara D.", (19, 19), (2, 3)),
        ("Teresa I.", (8, 2), (15, 18)),
        ("Javier R.", (13, 17), (7, 5)),
        ("Monica B.", (4, 1), (16, 11)),
        ("Pedro Z.", (17, 9), (9, 4)),
        ("Laura E.", (6, 14), (1, 8)),
        ("Ricardo N.", (10, 19), (18, 6)),
        ("Vanessa K.", (2, 7), (14, 1)),
        ("Oscar F.", (16, 16), (5, 5)),
        ("Nuria J.", (9, 9), (1, 1)),
    ]
    
    return datos_taxis, datos_clientes

def main():
    """Función principal para configurar y ejecutar la simulación."""
    
    # Usar un formato de log más limpio
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("\n" + "="*80)
    print("      *** INICIO DE LA SIMULACIÓN UNIETAXI - JORNADA 10:00:00 a 00:00:00 ***")
    print("="*80)

    # Inicializar el Sistema de Atención
    sistema_central = SistemaAtencion(HORA_INICIO, HORA_FIN)
    
    # Evento para controlar la ejecución de los Taxis (detención al final del día)
    reloj_running = threading.Event()
    reloj_running.set() 
    
    datos_taxis, datos_clientes = inicializar_datos()
    
    # --- 1. Lanzar el Hilo del Reloj ---
    hilo_reloj = RelojSistema(sistema_central, DURACION_REAL_SIMULACION)
    hilo_reloj.start()
    
    # *** PAUSA CRÍTICA: Permite que el reloj avance antes de que el primer cliente solicite ***
    time.sleep(1.5) 
    
    # --- 2. Crear y lanzar los Hilos Taxi ---
    hilos_taxis = []
    for id_vehiculo, marca, placa, ubicacion in datos_taxis:
        taxi = Taxi(id_vehiculo, marca, placa, ubicacion, sistema_central, reloj_running)
        hilos_taxis.append(taxi)
        taxi.start()
    
    # --- 3. Distribuir Clientes a lo largo del día (Demanda Aleatoria) ---
    hilos_clientes = []
    
    tiempo_total_disponible = DURACION_REAL_SIMULACION
    tiempo_transcurrido_real = 1.5 # Empezamos después de la pausa inicial

    clientes_pendientes = datos_clientes[:]
    random.shuffle(clientes_pendientes) 
    
    logging.info(f"\n*** La simulación se ejecutará durante {DURACION_REAL_SIMULACION} segundos. Los clientes aparecerán aleatoriamente. ***")

    for nombre, origen, destino in clientes_pendientes:
        
        # Calcular un tiempo de espera aleatorio para que los clientes se espacien
        clientes_restantes = len(clientes_pendientes) - clientes_pendientes.index((nombre, origen, destino))
        
        # Tiempo promedio para lanzar los clientes restantes, ajustado para no exceder DURACION_REAL_SIMULACION
        tiempo_restante_promedio = (tiempo_total_disponible - tiempo_transcurrido_real) / (clientes_restantes + 1)
        
        # Espera aleatoria: entre 0.5s y el tiempo promedio restante (máximo 5s para evitar bloqueos)
        tiempo_espera_real = random.uniform(0.5, min(5.0, tiempo_restante_promedio * 1.5))

        
        time.sleep(tiempo_espera_real)
        tiempo_transcurrido_real += tiempo_espera_real
        
        # Detener la distribución si el reloj simulado o real se ha detenido
        if not reloj_running.is_set() or not hilo_reloj.running.is_set():
            break

        cliente = Cliente(nombre, origen, destino, sistema_central)
        hilos_clientes.append(cliente)
        cliente.start()
    
    
    logging.info("\n*** Todos los clientes han sido lanzados. Esperando fin de jornada. ***")
    
    # Esperar a que el Hilo del Reloj termine (Medianoche o límite real)
    hilo_reloj.join()
    
    # Detener Taxis y clientes que sigan en espera
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
    # La configuración de logging en __name__ == "__main__" es redundante si se usa al inicio de main()
    # Dejamos la configuración simple para que no interfiera con los logs de los hilos.
    logging.basicConfig(level=logging.INFO, format='%(message)s') 
    main()