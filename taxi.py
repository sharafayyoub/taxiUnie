# taxi.py
import threading
import time
import logging

class Taxi(threading.Thread):
    """Representa un taxi en el sistema UNIETAXI."""
    def __init__(self, id_vehiculo, marca, placa, ubicacion_inicial, sistema_atencion, duracion_simulacion):
        super().__init__(name=f"Taxi-{id_vehiculo}")
        self.id_vehiculo = id_vehiculo
        self.marca = marca
        self.placa = placa
        self.ubicacion_actual = ubicacion_inicial
        self.sistema_atencion = sistema_atencion
        self.ganancia_total = 0
        self.cliente_actual = None
        self.ejecutando = threading.Event()
        self.ejecutando.set()
        self.duracion_simulacion = duracion_simulacion

    def run(self):
        """Simula el ciclo de vida del taxi: busca clientes, viaja, repite."""
        
        tiempo_inicio = time.time()
        
        # Bucle de trabajo continuo
        while self.ejecutando.is_set() and (time.time() - tiempo_inicio < self.duracion_simulacion):
            
            # 1. Buscar Cliente
            self.cliente_actual = self.sistema_atencion.buscar_y_asignar_cliente(self)
            
            if self.cliente_actual:
                cliente = self.cliente_actual
                
                # 2. Recoger al Cliente
                logging.info(f"Taxi {self.id_vehiculo}: Se dirige a recoger al cliente {cliente.nombre} en {cliente.coordenadas_origen}.")
                
                # Simular el viaje vacío (distancia de taxi a cliente)
                distancia_vacio, _ = self.sistema_atencion.calcular_tarifa_y_movimiento(self.ubicacion_actual, cliente.coordenadas_origen)
                self._simular_movimiento(distancia_vacio)
                self.ubicacion_actual = cliente.coordenadas_origen
                
                logging.info(f"Taxi {self.id_vehiculo}: ha recogido al cliente {cliente.nombre}. Inicia viaje a {cliente.coordenadas_destino}.")
                cliente.esta_en_taxi.set() # Notifica al cliente que ha sido recogido
                
                # 3. Viaje con Cliente
                distancia_viaje, costo_viaje = self.sistema_atencion.calcular_tarifa_y_movimiento(self.ubicacion_actual, cliente.coordenadas_destino)
                
                self._simular_movimiento(distancia_viaje)
                self.ubicacion_actual = cliente.coordenadas_destino
                
                # 4. Finalizar Viaje
                self.ganancia_total += costo_viaje
                cliente.marcar_como_atendido()
                
                logging.info(f"Taxi {self.id_vehiculo}: ha dejado al cliente {cliente.nombre} en {cliente.coordenadas_destino}. Costo del viaje: {costo_viaje} Euros.")
                self.cliente_actual = None
                time.sleep(0.5) # Simular tiempo para calificación/pago

            else:
                # No hay clientes, espera un momento y vuelve a buscar
                time.sleep(1)
        
        logging.info(f"Taxi {self.id_vehiculo}: Fin de la jornada de trabajo.")


    def _simular_movimiento(self, distancia):
        """Simula el tiempo de viaje basado en la distancia (1 unidad de distancia = 1 segundo)."""
        if distancia > 0:
            tiempo_viaje = max(1, distancia / 2) # Velocidad: 2 unidades/seg, mínimo 1 seg.
            time.sleep(tiempo_viaje) # Simulación de tiempo real de movimiento
            # Simulación de la coordenada final (por simplicidad, actualizamos al final del viaje)