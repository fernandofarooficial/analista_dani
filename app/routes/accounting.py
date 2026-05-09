from flask import Blueprint, render_template, request
from datetime import date, datetime
from sqlalchemy import extract, func
from app.extensions import db
from app.models import Agendamento

accounting_bp = Blueprint('accounting', __name__, url_prefix='/m/contabil')


@accounting_bp.route('/')
def report():
    hoje = date.today()
    modo = request.args.get('modo', 'mes')  # 'mes' ou 'periodo'

    if modo == 'periodo':
        inicio_str = request.args.get('inicio', '')
        fim_str = request.args.get('fim', '')
        try:
            inicio = datetime.strptime(inicio_str, '%Y-%m-%d')
            fim = datetime.strptime(fim_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            inicio = datetime(hoje.year, hoje.month, 1)
            fim = datetime(hoje.year, hoje.month, hoje.day, 23, 59, 59)
    else:
        mes = int(request.args.get('mes', hoje.month))
        ano = int(request.args.get('ano', hoje.year))
        inicio = datetime(ano, mes, 1)
        import calendar
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)

    agendamentos = (
        Agendamento.query
        .filter(
            Agendamento.confirmado == True,
            Agendamento.data_hora >= inicio,
            Agendamento.data_hora <= fim,
        )
        .order_by(Agendamento.data_hora)
        .all()
    )

    total_consulta = sum(float(a.valor_consulta or 0) for a in agendamentos)
    total_custo = sum(float(a.valor_custo or 0) for a in agendamentos)

    meses = _meses_disponiveis()

    return render_template(
        'accounting/report.html',
        agendamentos=agendamentos,
        total_consulta=total_consulta,
        total_custo=total_custo,
        total_geral=total_consulta + total_custo,
        inicio=inicio,
        fim=fim,
        modo=modo,
        mes_selecionado=inicio.month,
        ano_selecionado=inicio.year,
        meses=meses,
        hoje=hoje,
    )


def _meses_disponiveis():
    year_col = extract('year', Agendamento.data_hora)
    month_col = extract('month', Agendamento.data_hora)
    resultado = db.session.query(
        year_col.label('ano'),
        month_col.label('mes'),
    ).group_by(year_col, month_col).order_by(year_col.desc(), month_col.desc()).limit(24).all()
    return [(int(r.ano), int(r.mes)) for r in resultado]
