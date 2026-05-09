from flask import Blueprint, render_template, redirect, url_for, current_app, make_response
from datetime import datetime, date
from sqlalchemy import extract
from app.extensions import db
from app.models import Paciente, Agendamento

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))


@main_bp.route('/sw.js')
def service_worker():
    """Serve o service worker com escopo correto para o prefixo do app."""
    resp = make_response(current_app.send_static_file('sw.js'))
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@main_bp.route('/m/')
def dashboard():
    hoje = date.today()
    agora = datetime.utcnow()

    # Próximos agendamentos (7 dias)
    proximos = (
        Agendamento.query
        .filter(Agendamento.data_hora >= agora)
        .order_by(Agendamento.data_hora)
        .limit(10)
        .all()
    )

    # Aniversariantes do dia
    aniversariantes = (
        Paciente.query
        .filter(
            Paciente.ativo == True,
            Paciente.data_nascimento != None,
            extract('month', Paciente.data_nascimento) == hoje.month,
            extract('day', Paciente.data_nascimento) == hoje.day,
        )
        .all()
    )

    # Totais do mês corrente (confirmados)
    from sqlalchemy import func
    totais = db.session.query(
        func.sum(Agendamento.valor_consulta),
        func.sum(Agendamento.valor_custo),
    ).filter(
        Agendamento.confirmado == True,
        extract('month', Agendamento.data_hora) == hoje.month,
        extract('year', Agendamento.data_hora) == hoje.year,
    ).first()

    total_consulta = float(totais[0] or 0)
    total_custo = float(totais[1] or 0)

    total_pacientes = Paciente.query.filter_by(ativo=True).count()

    return render_template(
        'index.html',
        proximos=proximos,
        aniversariantes=aniversariantes,
        total_consulta=total_consulta,
        total_custo=total_custo,
        total_geral=total_consulta + total_custo,
        total_pacientes=total_pacientes,
        mes_atual=hoje.strftime('%B/%Y'),
    )
