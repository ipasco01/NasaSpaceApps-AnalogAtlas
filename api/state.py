"""
Estado compartido de la aplicación API.
Evita imports circulares entre main.py y las rutas.
"""

from services.motor_service import MotorService

motor_service: MotorService = None
