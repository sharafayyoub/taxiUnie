# sistema_atencion.py
import threading
import math
import time
import logging
from datetime import datetime, timedelta
import random
import math

# Configuración básica del logging para que los mensajes de los hilos se vean claros
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')

class SistemaAtencion:
    """
    Simula el Sistema Central de Atención al Cliente UNIETAXI.
    Gestión de clientes, match y reloj del sistema.
    """
    def __init__(self, hora_inicio, hora_fin):
        self.clientes_en_espera = []
        # Semáforo para proteger el acceso a la lista de espera (Recurso Crítico)
        self.lock = threading.Lock() 
        self.viajes_completados = []
        
        # Gestión del tiempo simulado
        self.hora_simulada = hora_inicio
        self.hora_fin = hora_fin
        # Factor de aceleración: 800 segundos simulados por 1 segundo real (~13 minutos/segundo)
        self.factor_aceleracion = 800 

        logging.info(f"Sistema Central de Atención UNIETAXI iniciado. Hora simulada: {self.hora_simulada.strftime('%H:%M:%S')}")

    def avanzar_tiempo(self, segundos_reales):
        """Avanza el tiempo simulado."""
        delta_simulado = timedelta(seconds=segundos_reales * self.factor_aceleracion)
        self.hora_simulada += delta_simulado
        
        if self.hora_simulada > self.hora_fin:
            self.hora_simulada = self.hora_fin
            return False
        return True

    def get_tiempo_simulado(self):
        """Retorna la hora simulada actual."""
        return self.hora_simulada

    def registrar_cliente(self, cliente):
        """Registra un nuevo cliente en la lista de espera."""
        with self.lock: # Sección crítica
            if cliente not in self.clientes_en_espera:
                self.clientes_en_espera.append(cliente)
                logging.info(f"[ {self.hora_simulada.strftime('%H:%M:%S')} ] 🧍 Cliente {cliente.nombre}: Solicita servicio en {cliente.coordenadas_origen}.")
        # 

    def buscar_y_asignar_cliente(self, taxi):
        """Busca el cliente más cercano y realiza la asignación."""
        cliente_asignado = None
        min_distancia = float('inf')

        # Implementación de la Sección Crítica para el recurso clientes_en_espera
        with self.lock: 
            if not self.clientes_en_espera:
                return None

            # Buscar el cliente más cercano
            for cliente in self.clientes_en_espera:
                distancia = self._calcular_distancia(taxi.ubicacion_actual, cliente.coordenadas_origen)
                # Si la distancia es igual, el documento sugiere desempatar por calificación, 
                # pero aquí usamos solo la distancia mínima por simplicidad.
                if distancia < min_distancia: 
                    min_distancia = distancia
                    cliente_asignado = cliente
            
            # Asignar y remover
            if cliente_asignado:
                self.clientes_en_espera.remove(cliente_asignado)
                cliente_asignado.hora_recogida_simulada = self.get_tiempo_simulado() 
                
                logging.info(f"[ {self.hora_simulada.strftime('%H:%M:%S')} ] *** ASIGNACIÓN: {taxi.id_vehiculo} -> {cliente_asignado.nombre}. Distancia a recoger: {min_distancia:.2f} unidades.")
        
        return cliente_asignado

    def _calcular_distancia(self, pos1, pos2):
        """Calcula la distancia euclidiana entre dos puntos (coordenadas x, y)."""
        # Distancia entre (x1, y1) y (x2, y2) es sqrt((x2-x1)^2 + (y2-y1)^2)
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def calcular_costo_y_tiempo(self, pos_origen, pos_destino):
        """
        Calcula la distancia, costo (1 unidad = 1€), tiempo de viaje simulado 
        y el tiempo REAL que el hilo debe dormir para sincronización.
        """
        distancia = self._calcular_distancia(pos_origen, pos_destino)
        costo_total = round(distancia)
        
        # Base de velocidad (unidades/minuto)
        vel_unid_min_base = 2.0 

        h = self.hora_simulada.hour
        
        # Ajuste de velocidad basado en la hora simulada (simulando tráfico)
        if 10 <= h < 16: # Mañana a Mediodía
            media = 1.0 
        elif 16 <= h < 20: # Hora pico (16:00 a 20:00)
            media = 0.8 # Velocidad base reducida
        else: # Noche (20:00 a 00:00)
            media = 1.1 # Velocidad base aumentada
            
        # Velocidad real (unidades/minuto) con ruido gaussiano
        # Utilizamos la media * base para obtener el centro y aseguramos que sea >= 0.5
        desviacion = 0.15 
        vel_unid_min_efectiva = max(0.5, random.gauss(media * vel_unid_min_base, desviacion)) 
        
        # Tiempo simulado en minutos y luego en segundos
        minutos = distancia / vel_unid_min_efectiva if vel_unid_min_efectiva > 0 else distancia
        
        # Convertir minutos a segundos simulados (mínimo 60 segundos simulados)
        tiempo_viaje_simulado = int(max(60, minutos * 60)) 
        
        # CÁLCULO CRÍTICO: Tiempo real de espera para el hilo (el taxi)
        tiempo_viaje_real = tiempo_viaje_simulado / self.factor_aceleracion

        # Devolvemos 4 valores
        return distancia, costo_total, tiempo_viaje_simulado, tiempo_viaje_real

    def registrar_viaje_completo(self, taxi, cliente, costo, duracion_simulada, hora_fin_simulada):
        """Registra un viaje completado si la hora de fin es antes de medianoche."""
        
        # Condición: no registrar si el viaje terminó después de la medianoche
        if hora_fin_simulada > self.hora_fin:
             logging.warning(f"[ {hora_fin_simulada.strftime('%H:%M:%S')} ] ❌ VIAJE NO REGISTRADO: El viaje de {taxi.id_vehiculo} con {cliente.nombre} finalizó después de medianoche. Contará para el día siguiente.")
             return False

        with self.lock:
            self.viajes_completados.append({
                'taxi_id': taxi.id_vehiculo,
                'cliente_nombre': cliente.nombre,
                'costo': costo,
                'hora_recogida': cliente.hora_recogida_simulada.strftime('%H:%M:%S'),
                'hora_llegada': hora_fin_simulada.strftime('%H:%M:%S'),
            })
        return True