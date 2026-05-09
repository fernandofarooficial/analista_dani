import requests
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


def send_whatsapp(phone: str, message: str, app=None) -> bool:
    """
    Envia mensagem WhatsApp via Evolution API (configurada nas settings).
    Retorna True se enviou com sucesso, False caso contrário.
    """
    if app:
        with app.app_context():
            return _send(phone, message)
    return _send(phone, message)


def _send(phone: str, message: str) -> bool:
    from app.models import Configuracao
    api_url = Configuracao.get('whatsapp_api_url', '').strip()
    api_key = Configuracao.get('whatsapp_api_key', '').strip()
    instance = Configuracao.get('whatsapp_instance', 'daniapp').strip()

    digits = ''.join(c for c in phone if c.isdigit())
    if not digits.startswith('55'):
        digits = '55' + digits

    if api_url and api_key:
        return _send_evolution(api_url, api_key, instance, digits, message)

    # Fallback: Callmebot (somente para o telefone cadastrado nas configs)
    callmebot_phone = Configuracao.get('callmebot_phone', '').strip()
    callmebot_key = Configuracao.get('callmebot_api_key', '').strip()
    if callmebot_key and digits == callmebot_phone:
        return _send_callmebot(digits, message, callmebot_key)

    logger.warning('WhatsApp nao configurado. URL gerada: %s', wa_me_link(phone, message))
    return False


def _send_evolution(api_url: str, api_key: str, instance: str, phone: str, message: str) -> bool:
    url = f'{api_url.rstrip("/")}/message/sendText/{instance}'
    headers = {'apikey': api_key, 'Content-Type': 'application/json'}
    payload = {'number': phone, 'text': message}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info('WhatsApp enviado via Evolution API para %s', phone)
        return True
    except Exception as e:
        logger.error('Erro Evolution API: %s', e)
        return False


def _send_callmebot(phone: str, message: str, api_key: str) -> bool:
    url = f'https://api.callmebot.com/whatsapp.php?phone={phone}&text={quote(message)}&apikey={api_key}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        logger.info('WhatsApp enviado via Callmebot para %s', phone)
        return True
    except Exception as e:
        logger.error('Erro Callmebot: %s', e)
        return False


def wa_me_link(phone: str, message: str) -> str:
    digits = ''.join(c for c in phone if c.isdigit())
    if not digits.startswith('55'):
        digits = '55' + digits
    return f'https://wa.me/{digits}?text={quote(message)}'


def notify_psicanal(message: str, app=None) -> bool:
    """Envia notificação para a psicanalista via Callmebot."""
    def _notify():
        from app.models import Configuracao
        phone = Configuracao.get('callmebot_phone', '').strip()
        key = Configuracao.get('callmebot_api_key', '').strip()
        if not phone or not key:
            logger.warning('Callmebot nao configurado para notificacoes internas.')
            return False
        return _send_callmebot(phone, message, key)

    if app:
        with app.app_context():
            return _notify()
    return _notify()
