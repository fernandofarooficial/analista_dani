from flask import Blueprint, request, redirect, url_for, flash
from app.extensions import db
from app.models import NotaPaciente, Paciente

notes_bp = Blueprint('notes', __name__, url_prefix='/m')


@notes_bp.route('/pacientes/<int:pid>/notas', methods=['POST'])
def create(pid):
    Paciente.query.get_or_404(pid)
    texto = request.form.get('texto', '').strip()
    if not texto:
        flash('A nota não pode estar vazia.', 'warning')
        return redirect(url_for('patients.detail', id=pid) + '#notas')
    nota = NotaPaciente(paciente_id=pid, texto=texto)
    db.session.add(nota)
    db.session.commit()
    flash('Nota adicionada.', 'success')
    return redirect(url_for('patients.detail', id=pid) + '#notas')


@notes_bp.route('/notas/<int:id>/excluir', methods=['POST'])
def delete(id):
    nota = NotaPaciente.query.get_or_404(id)
    pid = nota.paciente_id
    db.session.delete(nota)
    db.session.commit()
    flash('Nota removida.', 'info')
    return redirect(url_for('patients.detail', id=pid) + '#notas')
