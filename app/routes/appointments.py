from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.utils import now_sp
from app.extensions import db
from app.models import Agendamento, Paciente, Configuracao
from app.whatsapp import wa_me_link

appointments_bp = Blueprint('appointments', __name__, url_prefix='/m/agenda')


@appointments_bp.route('/')
def list():
    filtro = request.args.get('filtro', 'proximos')
    agora = now_sp()

    if filtro == 'anteriores':
        agendamentos = (
            Agendamento.query
            .filter(Agendamento.data_hora < agora)
            .order_by(Agendamento.data_hora.desc())
            .limit(50).all()
        )
    elif filtro == 'todos':
        agendamentos = Agendamento.query.order_by(Agendamento.data_hora.desc()).limit(100).all()
    else:
        agendamentos = (
            Agendamento.query
            .filter(Agendamento.data_hora >= agora)
            .order_by(Agendamento.data_hora)
            .limit(50).all()
        )

    return render_template('appointments/list.html', agendamentos=agendamentos, filtro=filtro)


@appointments_bp.route('/novo', methods=['GET', 'POST'])
@appointments_bp.route('/novo/<int:pid>', methods=['GET', 'POST'])
def new(pid=None):
    pacientes = Paciente.query.filter_by(ativo=True).order_by(Paciente.nome_completo).all()
    valor_consulta_padrao = Configuracao.get('valor_consulta', '200.00')
    valor_custo_padrao = Configuracao.get('valor_custo', '0.00')

    if request.method == 'POST':
        ag = _agendamento_from_form(Agendamento())
        db.session.add(ag)
        db.session.commit()
        flash('Consulta agendada com sucesso!', 'success')
        return redirect(url_for('appointments.list'))

    paciente_pre = db.session.get(Paciente, pid) if pid else None
    return render_template(
        'appointments/form.html',
        agendamento=None,
        pacientes=pacientes,
        paciente_pre=paciente_pre,
        valor_consulta_padrao=valor_consulta_padrao,
        valor_custo_padrao=valor_custo_padrao,
    )


@appointments_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def edit(id):
    ag = db.get_or_404(Agendamento, id)
    pacientes = Paciente.query.filter_by(ativo=True).order_by(Paciente.nome_completo).all()

    if request.method == 'POST':
        _agendamento_from_form(ag)
        db.session.commit()
        flash('Agendamento atualizado!', 'success')
        return redirect(url_for('appointments.list'))

    return render_template('appointments/form.html', agendamento=ag, pacientes=pacientes,
                           paciente_pre=ag.paciente, valor_consulta_padrao=ag.valor_consulta,
                           valor_custo_padrao=ag.valor_custo)


@appointments_bp.route('/<int:id>/confirmar', methods=['POST'])
def confirm(id):
    ag = db.get_or_404(Agendamento, id)
    ag.confirmado = not ag.confirmado
    db.session.commit()
    status = 'confirmada' if ag.confirmado else 'desconfirmada'
    flash(f'Consulta {status}.', 'success')
    return redirect(request.referrer or url_for('appointments.list'))


@appointments_bp.route('/<int:id>/excluir', methods=['POST'])
def delete(id):
    ag = db.get_or_404(Agendamento, id)
    db.session.delete(ag)
    db.session.commit()
    flash('Agendamento removido.', 'info')
    return redirect(url_for('appointments.list'))


@appointments_bp.route('/<int:id>/whatsapp-lembrete')
def whatsapp_lembrete(id):
    ag = db.get_or_404(Agendamento, id)
    p = ag.paciente
    if not p or not p.telefone:
        flash('Paciente sem telefone cadastrado.', 'warning')
        return redirect(url_for('appointments.list'))
    data_str = ag.data_hora.strftime('%d/%m/%Y às %H:%M')
    msg = (
        f'Olá, {p.nome_exibicao}! 😊\n'
        f'Lembrete da sua consulta em *{data_str}*.\n'
        f'Qualquer dúvida, entre em contato. Até lá! 🌸'
    )
    link = wa_me_link(p.telefone, msg)
    return redirect(link)


def _agendamento_from_form(ag: Agendamento) -> Agendamento:
    ag.paciente_id = int(request.form.get('paciente_id', 0))
    dh = request.form.get('data_hora', '').strip()
    if dh:
        try:
            ag.data_hora = datetime.fromisoformat(dh)
        except ValueError:
            pass
    try:
        ag.valor_consulta = float(request.form.get('valor_consulta', '0').replace(',', '.'))
    except ValueError:
        ag.valor_consulta = 0
    try:
        ag.valor_custo = float(request.form.get('valor_custo', '0').replace(',', '.'))
    except ValueError:
        ag.valor_custo = 0
    ag.confirmado = request.form.get('confirmado') == 'on'
    ag.observacoes = request.form.get('observacoes', '').strip() or None
    return ag
