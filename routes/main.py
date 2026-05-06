from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db_manager, obtener_alumnos_por_anio, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    if 'logged_in' in session:
        return redirect(url_for('main.home'))
    else:
        return redirect(url_for('auth.login'))

@main_bp.route("/home")
@login_required
def home():
    anio = request.args.get('anio', '')
    alumnos_actuales = obtener_alumnos_por_anio()
    alumnos = alumnos_actuales.get(anio, [])
    votos_bd = db_manager.obtener_votos_por_anio(anio) if anio else {}
    ya_votaron = set(votos_bd.keys())
    
    return render_template("home.html", 
                         alumnos=alumnos, 
                         ya_votaron=ya_votaron, 
                         anio=anio, 
                         alumnos_por_anio=alumnos_actuales,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))
