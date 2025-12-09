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
        self.esta_en_taxi = threading.Event() # Evento para esperar a ser recogido
        self.fue_atendido = False

    def run(self):
        """Simula el ciclo de vida del cliente: solicita y espera."""
        # El cliente solicita el servicio.
        self.sistema_atencion.registrar_cliente(self)
        
        # El cliente espera a ser atendido por un taxi (simulamos la espera)
        self.esta_en_taxi.wait() # Bloquea hasta que un taxi lo recoge y establece este evento
        
        if self.fue_atendido:
            logging.info(f"Cliente {self.nombre} ha finalizado su viaje y califica el servicio.")

    def marcar_como_atendido(self):
        """Método llamado por el taxi para indicar que el cliente ha sido atendido."""
        self.fue_atendido = True
        self.esta_en_taxi.set() # Desbloquea el hilo del cliente