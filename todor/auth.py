from flask import (
    Blueprint, render_template, request, url_for, redirect, flash, session, g
    )

from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from todor import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username, generate_password_hash(password))

        error = None

        #consultamos en la BD si existe ese usario que se quiere registrar
        user_name = User.query.filter_by(username=username).first()
        if user_name == None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            error = f'El usuario {username} ya esta registrado'

        flash(error)
        
    return render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        #Validar datos
        user = User.query.filter_by(username=username).first()
        if user == None:
            error = 'Nombre de usuario incorrecto'
        elif not check_password_hash(user.password, password):
            error = 'Contraseña incorrecta'
        
        #Iniciar sesion
        if error is None:
            session.clear() #si hay sesion, la cerramos
            session['user_id'] = user.id
            return redirect(url_for('todo.index'))

        flash(error)
    return render_template('auth/login.html')


#Mantener sesion iniciada
@bp.before_app_request #para que se ejecute antes de cada peticion dentro de la app
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id) #obtener id del usuario logeado o si no existe, error 404


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


import functools

#funcion decoradora para vistas que requieran iniciar sesion
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view