from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Paciente
from app.whatsapp import wa_me_link

patients_bp = Blueprint('patients', __name__, url_prefix='/m/pacientes')

_PER_PAGE = 20


@patients_bp.route('/')
def list():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Paciente.query.filter_by(ativo=True)
    if q:
        query = query.filter(
            db.or_(
                Paciente.nome_completo.ilike(f'%{q}%'),
                Paciente.nome.ilike(f'%{q}%'),
                Paciente.cpf.ilike(f'%{q}%'),
                Paciente.telefone.ilike(f'%{q}%'),
            )
        )
    paginacao = query.order_by(Paciente.nome_completo).paginate(page=page, per_page=_PER_PAGE, error_out=False)
    return render_template('patients/list.html', pacientes=paginacao.items, paginacao=paginacao, q=q)


@patients_bp.route('/novo', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        p = _paciente_from_form(Paciente())
        db.session.add(p)
        db.session.commit()
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('patients.detail', id=p.id))
    return render_template('patients/form.html', paciente=None)


@patients_bp.route('/<int:id>')
def detail(id):
    p = db.get_or_404(Paciente, id)
    return render_template('patients/detail.html', paciente=p)


@patients_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def edit(id):
    p = db.get_or_404(Paciente, id)
    if request.method == 'POST':
        _paciente_from_form(p)
        db.session.commit()
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('patients.detail', id=p.id))
    return render_template('patients/form.html', paciente=p)


@patients_bp.route('/<int:id>/whatsapp-parabens')
def whatsapp_parabens(id):
    p = db.get_or_404(Paciente, id)
    if not p.telefone:
        flash('Paciente sem telefone cadastrado.', 'warning')
        return redirect(url_for('main.dashboard'))
    msg = (
        f'Parabéns, {p.nome_exibicao}! 🎉\n'
        f'Desejo a você um dia muito especial. Muita saúde, amor e alegrias hoje e sempre.\n'
        f'Com carinho, Dani ❤️'
    )
    return redirect(wa_me_link(p.telefone, msg))


@patients_bp.route('/<int:id>/excluir', methods=['POST'])
def delete(id):
    p = db.get_or_404(Paciente, id)
    p.ativo = False
    db.session.commit()
    flash('Paciente inativado.', 'info')
    return redirect(url_for('patients.list'))


def _paciente_from_form(p: Paciente) -> Paciente:
    from datetime import date
    p.nome_completo = request.form.get('nome_completo', '').strip()
    p.nome = request.form.get('nome', '').strip() or None
    p.cpf = request.form.get('cpf', '').strip() or None
    p.rg = request.form.get('rg', '').strip() or None
    p.email = request.form.get('email', '').strip() or None
    p.telefone = request.form.get('telefone', '').strip() or None
    p.endereco = request.form.get('endereco', '').strip() or None
    p.numero = request.form.get('numero', '').strip() or None
    p.complemento = request.form.get('complemento', '').strip() or None
    p.bairro = request.form.get('bairro', '').strip() or None
    p.cidade = request.form.get('cidade', '').strip() or None
    p.estado = request.form.get('estado', '').strip() or None
    p.cep = request.form.get('cep', '').strip() or None
    p.escolaridade = request.form.get('escolaridade', '').strip() or None
    p.genero = request.form.get('genero', '').strip() or None
    p.estado_civil = request.form.get('estado_civil', '').strip() or None
    p.profissao = request.form.get('profissao', '').strip() or None
    p.naturalidade = request.form.get('naturalidade', '').strip() or None
    p.envia_parabens = request.form.get('envia_parabens') == 'on'

    dn = request.form.get('data_nascimento', '').strip()
    if dn:
        try:
            p.data_nascimento = date.fromisoformat(dn)
        except ValueError:
            pass
    else:
        p.data_nascimento = None

    return p
