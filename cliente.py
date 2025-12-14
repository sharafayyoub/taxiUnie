# cliente.py
import threading
import logging

class Cliente(threading.Thread):
    """Representa un cliente en el sistema UNIETAXI."""
    def __init__(self, nombre, coordenadas_origen, coordenadas_destino, sistema_atencion):
        super().__init__(name=f"Cliente-{nombre}")
        self.nombre = nombre
        self.coordenadas_origen = coordenadas_origen
        self.coordenadas_destino = coordenadas_destino
        self.sistema_atencion = sistema_atencion
        self.esta_en_taxi = threading.Event() 
        self.fue_atendido = False
        self.hora_recogida_simulada = None # Se llena cuando el sistema lo asigna

    def run(self):
        """Simula el ciclo de vida del cliente: solicita y espera."""
        self.sistema_atencion.registrar_cliente(self)
        self.esta_en_taxi.wait() 
        
        if self.fue_atendido:
            pass # El logging de la llegada se hace desde el Taxi para incluir la hora.

    def marcar_como_atendido(self):
        """Método llamado por el taxi para indicar que el cliente ha sido atendido."""
        self.fue_atendido = True
        self.esta_en_taxi.set() # Desbloquea el hilo del cliente