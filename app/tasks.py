import logging
from datetime import timedelta
from app.utils import now_sp

logger = logging.getLogger(__name__)


def check_birthdays(app):
    """Verifica aniversariantes do dia e envia alertas."""
    with app.app_context():
        from app.models import Paciente
        from app.whatsapp import send_whatsapp, notify_psicanal

        hoje = now_sp().date()
        pacientes = Paciente.query.filter(
            Paciente.ativo == True,
            Paciente.data_nascimento != None,
            db_extract('month', Paciente.data_nascimento) == hoje.month,
            db_extract('day', Paciente.data_nascimento) == hoje.day,
        ).all()

        for p in pacientes:
            nome = p.nome_exibicao
            logger.info('Aniversario hoje: %s', p.nome_completo)

            if p.envia_parabens and p.telefone:
                msg = (
                    f'Parabéns, {nome}! 🎉\n'
                    f'Desejamos a você um dia muito especial cheio de alegria e saúde.\n'
                    f'Com carinho, Dani ❤️'
                )
                enviado = send_whatsapp(p.telefone, msg, app=None)
                if not enviado:
                    logger.warning('Nao foi possivel enviar parabens para %s', p.nome_completo)

            # Sempre notifica a psicanalista
            notify_psicanal(
                f'🎂 Hoje é aniversário de {p.nome_completo}!'
                + ('' if p.envia_parabens else ' (não enviar parabéns automaticamente)'),
                app=None,
            )


def check_appointments_24h(app):
    """Envia lembrete WhatsApp para consultas nas próximas 24h."""
    with app.app_context():
        from app.models import Agendamento
        from app.whatsapp import send_whatsapp

        agora = now_sp()
        em_24h = agora + timedelta(hours=24)
        janela_inicio = em_24h - timedelta(minutes=30)
        janela_fim = em_24h + timedelta(minutes=30)

        agendamentos = Agendamento.query.filter(
            Agendamento.data_hora >= janela_inicio,
            Agendamento.data_hora <= janela_fim,
            Agendamento.whatsapp_enviado == False,
            Agendamento.confirmado == False,
        ).all()

        for ag in agendamentos:
            p = ag.paciente
            if not p or not p.telefone:
                continue
            data_str = ag.data_hora.strftime('%d/%m/%Y às %H:%M')
            msg = (
                f'Olá, {p.nome_exibicao}! 😊\n'
                f'Lembrete da sua consulta amanhã, *{data_str}*.\n'
                f'Qualquer dúvida, entre em contato. Até lá! 🌸'
            )
            enviado = send_whatsapp(p.telefone, msg, app=None)
            if enviado:
                ag.whatsapp_enviado = True
                from app.extensions import db
                db.session.commit()
                logger.info('Lembrete enviado para %s (agendamento %d)', p.nome_completo, ag.id)


def db_extract(field, column):
    from sqlalchemy import extract
    return extract(field, column)
