from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db_manager, obtener_alumnos_por_anio, login_required
from urllib.parse import unquote
from datetime import datetime

votacion_bp = Blueprint('votacion', __name__)

@votacion_bp.route('/votar/<anio>/<nombre>', methods=['GET', 'POST'])
@login_required
def votar(anio, nombre):
    # ... (impl del código movido de app.py) ...
    pass

@votacion_bp.route("/procesar_voto", methods=["POST"])
@login_required
def procesar_voto():
    # ... (impl del código movido de app.py) ...
    pass
