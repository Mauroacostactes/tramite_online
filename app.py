from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from models import db, User, SeUsuarioRegistro, SeUsuarioPerfil, PreTramiteVirt,PreEstado
import os
from datetime import datetime 
from sqlalchemy.exc import SQLAlchemyError




load_dotenv()
# Configuración de la base de datos desde el archivo .env
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['SECRET_KEY'] = os.urandom(24).hex()

login_manager = LoginManager(app)

# Añade overlaps para resolver la sobreposición
db.relationship('User.registros', overlaps="registros,usuario")

# Configuración del manejador de usuarios
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta de inicio/redirección
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar al usuario en la tabla se_usuario
        user_info = db.session.query(User).join(
            SeUsuarioRegistro, User.id_usuario == SeUsuarioRegistro.id_usuario
        ).filter(User.login == username).first()

        if user_info and user_info.check_password(password):
            print("¡Usuario encontrado y contraseña coinciden!")
            login_user(user_info)
            es_admin = any(perfil.id_perfil == 483 and perfil.fecha_baja is None for perfil in current_user.perfiles)
            print(f"¿Es administrador? {es_admin}")

            # Llamar a la función para obtener la lista de archivos PDF
            if es_admin:
                
                return redirect(url_for('mesaentrada', es_admin=es_admin,alert_type='success', alert_message='Inicio de sesión exitoso'))
            else:
                
                return redirect(url_for('subirpdf', es_admin=es_admin,alert_type='success', alert_message='Inicio de sesión exitoso'))
            
        else:
            print("¡Usuario no encontrado o contraseña no coincide!")
            return render_template('login.html', alert_type='error', alert_message='Nombre de usuario o contraseña incorrectos')

    return render_template('login.html')


# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', alert_type='info', alert_message='Has cerrado sesión'))


# Ruta de subida de archivos
@app.route('/subirpdf', methods=['GET', 'POST'])
@login_required
def subirpdf():
    mensaje = None
    error = None
    nombre_completo = (current_user.nombre+' '+current_user.apellido)
    nro_doc=(current_user.nro_doc)

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No se seleccionó ningún archivo'
        else:
            file = request.files['file']
            filename =(request.form['partida'].upper()+' '+request.form['tipo_de_tramite']+' '+current_user.nombre+' '+current_user.apellido)
            

            if file.filename == '':
                error = 'No se seleccionó ningún archivo'
            elif file and file.filename.endswith('.pdf'):
                directorio_escaneo = r'C:\Users\Admin\Desktop\Tramite\tramites'

                try:
                    

                    # Crear un nuevo registro en la tabla pre_tramite_virt
                    nuevo_tramite = PreTramiteVirt(
                        partida=request.form.get('partida'),
                        jurisdiccion=request.form.get('jurisdiccion'),
                        tipo_de_tramite=request.form.get('tipo_de_tramite'),
                        fecha_creacion=datetime.now(),  # Utiliza la fecha y hora actual
                        iniciador=nombre_completo,
                        nro_doc=nro_doc
                    )

                    db.session.add(nuevo_tramite)
                    db.session.commit()
                    filename =(str(nuevo_tramite.id_solicitud)+' '+request.form['partida'].upper()+' '+request.form['tipo_de_tramite']+' '+current_user.nombre+' '+current_user.apellido)
                    ruta_completa = os.path.join(directorio_escaneo, filename + '.pdf')
                    file.save(ruta_completa)

                    mensaje = 'Archivo PDF recibido correctamente y registro creado en la base de datos'
                except SQLAlchemyError as e:
                    # Hacer rollback en caso de excepción de SQLAlchemy
                    db.session.rollback()
                    error = f'Error al guardar el archivo: {str(e)}'
            else:
                error = 'El archivo seleccionado no es un PDF'

    return render_template('subirpdf.html', mensaje=mensaje, error=error)


# visualizar los pdf del usuario externo
@app.route('/vermipdf', methods=['GET', 'POST'])
@login_required
def vermipdf():
    nro_documento_deseado = current_user.nro_doc
    pre_tramites = PreTramiteVirt.query.filter_by(nro_doc=nro_documento_deseado).all()
    return render_template('subirpdf.html', pre_tramites=pre_tramites)


#Guardar observaciones en cada pre-tramite
@app.route('/guardar_observaciones', methods=['POST'])
@login_required
def guardar_observaciones():
    if request.method == 'POST':
        id_solicitud = request.form.get('id_solicitud')
        observaciones = request.form.get('observaciones')
        estado = request.form.get('estado')

        # Actualizar la base de datos con las observaciones
        tramite = PreTramiteVirt.query.filter_by(id_solicitud=id_solicitud).first()
        if tramite:
            tramite.observaciones = observaciones
            tramite.estado = estado
            db.session.commit()

            return jsonify({'message': 'Observaciones guardadas correctamente'})
        else:
            return jsonify({'error': 'Pre-Trámite no encontrado'}), 404

       

# Ruta principal con visualización de PDFs y manejo de archivos
@app.route('/mesaentrada', methods=['GET', 'POST'])
@login_required
def mesaentrada():
    trámites = PreTramiteVirt.query.all()
    return render_template('mesaentrada.html', trámites=trámites)



# Punto de entrada para ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
