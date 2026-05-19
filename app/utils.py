from datetime import datetime, date
import pytz

_SP = pytz.timezone('America/Sao_Paulo')

_MESES_PT = (
    '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
)


def now_sp() -> datetime:
    """Retorna datetime naive no fuso de São Paulo."""
    return datetime.now(_SP).replace(tzinfo=None)


def mes_pt(dt) -> str:
    """Nome do mês em português para um date ou datetime."""
    return _MESES_PT[dt.month]


def fmt_data(dt) -> str:
    """Formata date ou datetime como dd/mm/aaaa."""
    if dt is None:
        return ''
    return dt.strftime('%d/%m/%Y')


def fmt_datahora(dt) -> str:
    """Formata datetime como dd/mm/aaaa HH:MM."""
    if dt is None:
        return ''
    return dt.strftime('%d/%m/%Y %H:%M')
