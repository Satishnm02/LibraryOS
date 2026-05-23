from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, Admin

def create_app():
    app = Flask(
        __name__,
        template_folder=Config.TEMPLATE_FOLDER,
        static_folder=Config.STATIC_FOLDER
    )
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(uid):
        return Admin.query.get(int(uid))

    from routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    if not Admin.query.first():
        a = Admin(username='admin', email='admin@library.com')
        a.set_password('admin123')
        db.session.add(a)
        db.session.commit()
        print("✅ Admin seeded  →  admin / admin123")


if __name__ == '__main__':
    create_app().run(debug=True)