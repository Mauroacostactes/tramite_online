# models.py
import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey


db = SQLAlchemy()

# Definir el modelo para la tabla 'se_usuario'
class User(UserMixin, db.Model):
    __tablename__ = 'se_usuario'

    id_usuario = db.Column(db.BigInteger, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    sector = db.Column(db.String(255))
    id_tipo_doc = db.Column(db.String(10))
    nro_doc = db.Column(db.String(20))
    domicilio = db.Column(db.String(255))
    habilitado = db.Column(db.Boolean, nullable=False)
    cambio_pass = db.Column(db.Boolean)
    usuario_alta = db.Column(db.BigInteger, nullable=False)
    fecha_alta = db.Column(db.TIMESTAMP, nullable=False)
    usuario_modificacion = db.Column(db.BigInteger, nullable=False)
    fecha_modificacion = db.Column(db.TIMESTAMP, nullable=False)
    usuario_baja = db.Column(db.BigInteger)
    fecha_baja = db.Column(db.TIMESTAMP)
    cant_ingr_fallidos = db.Column(db.Numeric(2))
    id_sector = db.Column(db.Integer)
    id_isicat = db.Column(db.BigInteger)
    nombre_apellido_isicat = db.Column(db.String(100))
    login_isicat = db.Column(db.String(50))
    vigencia_desde_isicat = db.Column(db.Date)
    vigencia_hasta_isicat = db.Column(db.Date)

    perfiles = db.relationship('SeUsuarioPerfil', primaryjoin='User.id_usuario == SeUsuarioPerfil.id_usuario', back_populates='usuario')
    registros = db.relationship('SeUsuarioRegistro', back_populates='usuario', overlaps="registros,usuario")
    
    def check_password(self, password):
        # Obtener la contraseña más reciente del usuario
        latest_password_record = SeUsuarioRegistro.query.filter_by(id_usuario=self.id_usuario).order_by(SeUsuarioRegistro.fecha_operacion.desc()).first()

        if latest_password_record:
            # Utilizar MD5 para comparar contraseñas
            return latest_password_record.registro == calculate_md5_hash(password)
        else:
            # No hay registros de contraseña para el usuario
            return False


    # Añadir este método
    def get_id(self):
        return str(self.id_usuario)

    def __init__(self, login, password):
        self.login = login
        self.password_hash = generate_password_hash(password)

    @classmethod
    def find_by_login(cls, login):
        return cls.query.filter_by(login=login).first()
    
# Definir el calculador de md5
def calculate_md5_hash(input):
    md5 = hashlib.md5()
    md5.update(input.encode('utf-8'))
    return md5.hexdigest()


# Definir el modelo para la tabla 'se_usuario_registro'
class SeUsuarioRegistro(db.Model):
    __tablename__ = 'se_usuario_registro'

    id_usuario_registro = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('se_usuario.id_usuario'), nullable=False)
    registro = db.Column(db.String(255))
    usuario_operacion = db.Column(db.Integer, nullable=False)
    fecha_operacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    usuario = db.relationship('User', back_populates='registros', overlaps="registros,usuario")

class SeUsuarioPerfil(db.Model):
    __tablename__ = 'se_usuario_perfil'

    id_usuario_perfil = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('se_usuario.id_usuario'), nullable=False)
    id_perfil = db.Column(db.BigInteger, nullable=False)
    id_horario = db.Column(db.BigInteger, nullable=False)
    usuario_alta = db.Column(db.BigInteger, nullable=False)
    fecha_alta = db.Column(db.TIMESTAMP, nullable=False)
    usuario_baja = db.Column(db.BigInteger, nullable=True)
    fecha_baja = db.Column(db.TIMESTAMP, nullable=True)

    # Relaciones
    usuario = db.relationship('User', back_populates='perfiles')


class PreEstado(db.Model):
    __tablename__ = 'pre_estado'

    id_estado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estado = db.Column(db.String(40))


# Definir el modelo para la tabla 'pre_tramite_virt'
class PreTramiteVirt(db.Model):
    __tablename__ = 'pre_tramite_virt'

    id_solicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    partida = db.Column(db.String(20))
    jurisdiccion = db.Column(db.String(20))
    tipo_de_tramite = db.Column(db.String(20), CheckConstraint("tipo_de_tramite IN ('Valuacion_Fiscal', 'Reporte_Catastral', 'Copia_planos')"))
    fecha_creacion = db.Column(db.TIMESTAMP)
    iniciador = db.Column(db.String(20))
    nro_doc=db.Column(db.String(20))
    observaciones=db.Column(db.String(200))
    estado = db.Column(db.Integer, db.ForeignKey('pre_estado.id_estado'), default='1')

    # Relacion
    pre_estado = db.relationship('PreEstado', foreign_keys=[estado], primaryjoin="PreTramiteVirt.estado == PreEstado.id_estado")

    


