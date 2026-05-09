from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Anamnese, Paciente

anamnesis_bp = Blueprint('anamnesis', __name__, url_prefix='/m')


@anamnesis_bp.route('/pacientes/<int:pid>/anamnese/nova', methods=['GET', 'POST'])
def new(pid):
    paciente = Paciente.query.get_or_404(pid)
    if request.method == 'POST':
        a = _anamnese_from_form(Anamnese(paciente_id=pid))
        db.session.add(a)
        db.session.commit()
        flash('Ficha de anamnese criada!', 'success')
        return redirect(url_for('anamnesis.view', id=a.id))
    return render_template('anamnesis/form.html', anamnese=None, paciente=paciente)


@anamnesis_bp.route('/anamnese/<int:id>')
def view(id):
    a = Anamnese.query.get_or_404(id)
    return render_template('anamnesis/view.html', anamnese=a, paciente=a.paciente)


@anamnesis_bp.route('/anamnese/<int:id>/editar', methods=['GET', 'POST'])
def edit(id):
    a = Anamnese.query.get_or_404(id)
    if request.method == 'POST':
        _anamnese_from_form(a)
        db.session.commit()
        flash('Anamnese atualizada!', 'success')
        return redirect(url_for('anamnesis.view', id=a.id))
    return render_template('anamnesis/form.html', anamnese=a, paciente=a.paciente)


@anamnesis_bp.route('/anamnese/<int:id>/excluir', methods=['POST'])
def delete(id):
    a = Anamnese.query.get_or_404(id)
    pid = a.paciente_id
    db.session.delete(a)
    db.session.commit()
    flash('Anamnese removida.', 'info')
    return redirect(url_for('patients.detail', id=pid))


def _anamnese_from_form(a: Anamnese) -> Anamnese:
    fields = [
        'indicacao', 'fuma', 'bebe', 'drogas', 'vicios_compulsoes', 'fez_terapia_anterior',
        'conjuge', 'mae', 'pai', 'irmaos', 'ordem_filho', 'filhos',
        'queixa_principal', 'historico_queixa_atual',
        'hist_infancia', 'hist_adolescencia', 'hist_vida_adulta', 'hist_dinamica_familiar',
        'saude_medicacoes', 'saude_tratamentos_anteriores', 'saude_sono_alimentacao',
        'aparencia_atitude', 'hipotese_diagnostica', 'contratransferencia', 'prognostico_plano',
    ]
    for f in fields:
        setattr(a, f, request.form.get(f, '').strip() or None)
    return a
