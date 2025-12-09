# sistema_atencion.py
import threading
import math
import time
import logging

# Configuración básica del logging para que los mensajes de los hilos se vean claros
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')

class SistemaAtencion:
    """
    Simula el Sistema Central de Atención al Cliente UNIETAXI.
    Se encarga de gestionar la lista de clientes en espera y realizar el match cliente-taxi.
    """
    def __init__(self):
        # Recurso Crítico: Lista de clientes esperando asignación de taxi.
        self.clientes_en_espera = []
        # Semáforo para proteger el acceso al recurso crítico (lista de espera).
        self.lock = threading.Lock()
        logging.info("Sistema Central de Atención UNIETAXI inicializado.")

    def registrar_cliente(self, cliente):
        """Registra un nuevo cliente en la lista de espera."""
        with self.lock: # Seccion crítica: Acceso a clientes_en_espera
            if cliente not in self.clientes_en_espera:
                self.clientes_en_espera.append(cliente)
                logging.info(f"Cliente {cliente.nombre} ha entrado en la lista de espera en {cliente.coordenadas_origen}.")
        # 
    def buscar_y_asignar_cliente(self, taxi):
        """
        Busca el cliente más cercano al taxi dentro de la lista de espera
        y realiza la asignación (match) si hay clientes.
        Retorna el cliente asignado o None.
        """
        cliente_asignado = None
        min_distancia = float('inf')

        with self.lock: # Seccion crítica: Acceso y modificación de clientes_en_espera
            if not self.clientes_en_espera:
                return None

            # 1. Buscar el cliente más cercano (criterio de match)
            # El documento indica: "busca en un radio de 2 km" y selecciona el "más cercano"[cite: 40].
            # Aquí, por simplicidad, tomamos el más cercano de la lista.
            for cliente in self.clientes_en_espera:
                distancia = self._calcular_distancia(taxi.ubicacion_actual, cliente.coordenadas_origen)
                if distancia < min_distancia:
                    min_distancia = distancia
                    cliente_asignado = cliente
            
            # 2. Asignar y remover de la lista de espera
            if cliente_asignado:
                self.clientes_en_espera.remove(cliente_asignado)
                logging.info(f"*** ASIGNACIÓN: Taxi {taxi.id_vehiculo} asignado a cliente {cliente_asignado.nombre}. Distancia a recoger: {min_distancia:.2f} unidades.")
        
        return cliente_asignado

    def _calcular_distancia(self, pos1, pos2):
        """Calcula la distancia euclidiana entre dos puntos (coordenadas x, y)."""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def calcular_tarifa_y_movimiento(self, pos_origen, pos_destino):
        """
        Calcula la distancia y el costo (1 unidad = 1 Euro)
        Retorna (distancia, costo_total)
        """
        distancia = self._calcular_distancia(pos_origen, pos_destino)
        # 1 unidad de coordenada = 1 Euro de tarifa.
        costo_total = round(distancia) # Redondeamos la distancia para la tarifa

        return distancia, costo_total

    def get_estado_espera(self):
        """Retorna el número de clientes esperando."""
        with self.lock:
            return len(self.clientes_en_espera)