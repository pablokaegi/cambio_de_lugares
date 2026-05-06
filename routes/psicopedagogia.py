from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db_manager, login_required, role_required
# ... otros imports ...

psicopedagogia_bp = Blueprint('psicopedagogia', __name__)

@psicopedagogia_bp.route("/resultados")
@login_required  
def resultados():
    # ... mover lógica de resultados ...
    pass

@psicopedagogia_bp.route("/asignacion_bancos")
@login_required
def asignacion_bancos():
    # ... mover lógica de asignación bancos ...
    pass
