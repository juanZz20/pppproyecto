from .usuarios import usuarios_bp
from .catalogo import catalogo_bp
from .reporte import reporte_bp
from .login import login_bp


def registrar_rutas(app):
    app.register_blueprint(usuarios_bp,url_prefix='/usuarios')
    app.register_blueprint(catalogo_bp,url_prefix='/catalogo')
    app.register_blueprint(reporte_bp,url_prefix='/reporte')
    app.register_blueprint(login_bp,url_prefix="/login")

