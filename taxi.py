# taxi.py
import threading
import time
import logging
import random

class Taxi(threading.Thread):
    """Representa un taxi en el sistema UNIETAXI."""
    def __init__(self, id_vehiculo, marca, placa, ubicacion_inicial, sistema_atencion, reloj_running):
        super().__init__(name=f"Taxi-{id_vehiculo}")
        self.id_vehiculo = id_vehiculo
        self.marca = marca
        self.placa = placa
        self.ubicacion_actual = ubicacion_inicial
        self.sistema_atencion = sistema_atencion
        self.ganancia_total = 0
        self.cliente_actual = None
        self.reloj_running = reloj_running # Referencia al evento del main para saber si el tiempo corre
        self.num_viajes = 0
        self.calificacion_media = 0.0 # Calificación del día

    def run(self):
        """Ciclo de vida del taxi: busca, viaja, repite, hasta medianoche."""
        
        while self.reloj_running.is_set(): # Corre mientras el reloj del sistema esté activo
            
            # 1. Buscar Cliente
            self.cliente_actual = self.sistema_atencion.buscar_y_asignar_cliente(self)
            
            if self.cliente_actual:
                cliente = self.cliente_actual
                
                # --- A. Viaje vacío (Recogida) ---
                _, _, tiempo_vacio_simulado = self.sistema_atencion.calcular_costo_y_tiempo(self.ubicacion_actual, cliente.coordenadas_origen)
                
                logging.info(f"[ {self.sistema_atencion.get_tiempo_simulado().strftime('%H:%M:%S')} ] 🚗 {self.id_vehiculo} -> Recogida de {cliente.nombre}. Tiempo sim: {int(tiempo_vacio_simulado)}s.")
                
                # Simular tiempo real basado en el tiempo simulado del viaje
                tiempo_real_viaje = tiempo_vacio_simulado / self.sistema_atencion.factor_aceleracion
                self.sistema_atencion.avanzar_tiempo(tiempo_real_viaje)
                time.sleep(tiempo_real_viaje) 
                
                self.ubicacion_actual = cliente.coordenadas_origen
                logging.info(f"[ {self.sistema_atencion.get_tiempo_simulado().strftime('%H:%M:%S')} ] ✅ {self.id_vehiculo} recoge a {cliente.nombre}. Inicia viaje a {cliente.coordenadas_destino}.")
                cliente.esta_en_taxi.set() 

                # --- B. Viaje con Cliente (Entrega) ---
                distancia_viaje, costo_viaje, tiempo_viaje_simulado = self.sistema_atencion.calcular_costo_y_tiempo(self.ubicacion_actual, cliente.coordenadas_destino)
                
                # Simular tiempo real
                tiempo_real_viaje = tiempo_viaje_simulado / self.sistema_atencion.factor_aceleracion
                hora_inicio_viaje = self.sistema_atencion.get_tiempo_simulado()
                self.sistema_atencion.avanzar_tiempo(tiempo_real_viaje) # Avanza el reloj mientras el taxi "viaja"
                time.sleep(tiempo_real_viaje)
                
                hora_fin_viaje = self.sistema_atencion.get_tiempo_simulado()
                
                # 2. Finalizar Viaje
                self.ubicacion_actual = cliente.coordenadas_destino
                
                if self.sistema_atencion.registrar_viaje_completo(self, cliente, costo_viaje, tiempo_viaje_simulado, hora_fin_viaje):
                    self.ganancia_total += costo_viaje
                    self.num_viajes += 1
                    logging.info(f"[ {hora_fin_viaje.strftime('%H:%M:%S')} ] 🛬 {self.id_vehiculo} deja a {cliente.nombre}. Costo: {costo_viaje}€. Nueva Ubicación: {self.ubicacion_actual}")
                    
                cliente.marcar_como_atendido()
                self.cliente_actual = None
                time.sleep(0.5) # Pequeña pausa real para simular pago/descanso

            else:
                # No hay clientes. Espera 1 segundo real (3000 segundos simulados) y avanza el reloj.
                self.sistema_atencion.avanzar_tiempo(1)
                time.sleep(1)
        
        # Al finalizar el día, generar una calificación media aleatoria (1 a 5)
        self.calificacion_media = round(random.uniform(3.0, 5.0), 2)
        
        logging.info(f"--- 🛑 {self.id_vehiculo}: Cierre de Jornada. Total viajes: {self.num_viajes}. Ganancia final: {self.ganancia_total}€.")