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


def fmt_telefone(valor) -> str:
    """Formata número de telefone como (99) 9 9999-9999 (celular) ou (99) 9999-9999 (fixo)."""
    if not valor:
        return ''
    digits = ''.join(c for c in str(valor) if c.isdigit())
    # Remove código do país 55 se presente
    if len(digits) == 13 and digits.startswith('55'):
        digits = digits[2:]
    elif len(digits) == 12 and digits.startswith('55'):
        digits = digits[2:]
    if len(digits) == 11:
        return f'({digits[:2]}) {digits[2]} {digits[3:7]}-{digits[7:]}'
    if len(digits) == 10:
        return f'({digits[:2]}) {digits[2:6]}-{digits[6:]}'
    return valor
