from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Re-implementing helper to avoid circular imports if needed, 
# or import from app (but app imports routes -> circular).
# Better approach: Keep shared helpers in a utils.py
# For now, I will assume a simpler structure for the demo.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Debes iniciar sesión para acceder al sistema", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                flash("Debes iniciar sesión para acceder al sistema", "warning")
                return redirect(url_for('auth.login'))
            
            user_rol = session.get('rol', '')
            if user_rol not in roles:
                flash("No tienes permisos para acceder a esta sección", "error")
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app import USUARIOS_DOCENTES 
    if 'logged_in' in session:
        return redirect(url_for('home'))
        
    if request.method == "POST":
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario in USUARIOS_DOCENTES and USUARIOS_DOCENTES[usuario]['password'] == password:
            session['logged_in'] = True
            session['usuario'] = usuario
            session['rol'] = USUARIOS_DOCENTES[usuario]['rol']
            flash(f"¡Bienvenido/a {usuario}! ({USUARIOS_DOCENTES[usuario]['rol'].title()})", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    usuario = session.get('usuario', 'Usuario')
    session.clear()
    flash(f"¡Hasta luego {usuario}! Sesión cerrada exitosamente", "info")
    return redirect(url_for('auth.login'))
