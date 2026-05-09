from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Configuracao

settings_bp = Blueprint('settings', __name__, url_prefix='/m/config')

CHAVES = [
    ('valor_consulta', 'Valor Padrão da Consulta (R$)', 'number'),
    ('valor_custo', 'Valor Padrão do Custo (R$)', 'number'),
    ('psicanal_nome', 'Nome da Psicanalista', 'text'),
    ('psicanal_telefone', 'Telefone da Psicanalista', 'text'),
    ('whatsapp_api_url', 'Evolution API URL (ex: http://localhost:8080)', 'text'),
    ('whatsapp_api_key', 'Evolution API Key', 'text'),
    ('whatsapp_instance', 'Evolution API Instance', 'text'),
    ('callmebot_phone', 'Callmebot Telefone (com DDI, ex: 5511999999999)', 'text'),
    ('callmebot_api_key', 'Callmebot API Key', 'text'),
]


@settings_bp.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        for chave, _, _ in CHAVES:
            valor = request.form.get(chave, '').strip()
            Configuracao.set(chave, valor)
        flash('Configurações salvas!', 'success')
        return redirect(url_for('settings.form'))

    configs = {c.chave: c.valor for c in Configuracao.query.all()}
    return render_template('settings/form.html', chaves=CHAVES, configs=configs)
