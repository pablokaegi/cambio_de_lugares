"""
Archivo de entrada WSGI para cPanel/Passenger
Requerido por cPanel para servir aplicaciones Python
"""
from app import app as application

# El servidor Passenger buscará automáticamente la variable 'application'
if __name__ == '__main__':
    application.run()
