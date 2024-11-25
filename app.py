# app.py

from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa as extensões
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Registra as rotas de autenticação
        from routes import register_routes
        register_routes(app)

        # Registra as rotas do chat
        from routes_chat import chat_bp
        app.register_blueprint(chat_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
