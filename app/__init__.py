from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config
from app.extensions import db, scheduler


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Suporte a reverse proxy nginx: mantém SCRIPT_NAME, proto e host corretos
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.patients import patients_bp
    from app.routes.anamnesis import anamnesis_bp
    from app.routes.notes import notes_bp
    from app.routes.appointments import appointments_bp
    from app.routes.accounting import accounting_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(anamnesis_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        db.create_all()
        _seed_configuracoes()
        _start_scheduler(app)

    return app


def _seed_configuracoes():
    from app.models import Configuracao
    defaults = {
        'valor_consulta': '200.00',
        'valor_custo': '0.00',
        'whatsapp_api_url': '',
        'whatsapp_api_key': '',
        'whatsapp_instance': 'daniapp',
        'callmebot_phone': '',
        'callmebot_api_key': '',
        'psicanal_nome': 'Dani',
        'psicanal_telefone': '',
    }
    for chave, valor in defaults.items():
        if not Configuracao.query.filter_by(chave=chave).first():
            db.session.add(Configuracao(chave=chave, valor=valor))
    db.session.commit()


def _start_scheduler(app):
    if scheduler.running:
        return
    from app.scheduler import check_birthdays, check_appointments_24h
    scheduler.add_job(
        func=check_birthdays,
        args=[app],
        trigger='cron',
        hour=8,
        minute=0,
        id='check_birthdays',
        replace_existing=True,
    )
    scheduler.add_job(
        func=check_appointments_24h,
        args=[app],
        trigger='interval',
        hours=1,
        id='check_appointments_24h',
        replace_existing=True,
    )
    scheduler.start()
