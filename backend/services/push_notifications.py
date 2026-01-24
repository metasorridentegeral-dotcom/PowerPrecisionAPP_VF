"""
====================================================================
SERVIÇO DE PUSH NOTIFICATIONS - CREDITOIMO
====================================================================
Serviço para enviar notificações push via Web Push API.
====================================================================
"""

import logging
import json
from typing import Optional, List
from datetime import datetime, timezone

from database import db

logger = logging.getLogger(__name__)

# Nota: Para enviar notificações push reais, seria necessário:
# 1. Gerar VAPID keys (chaves públicas/privadas)
# 2. Instalar biblioteca pywebpush
# 3. Configurar as chaves no ambiente
#
# Por agora, este serviço prepara os dados e guarda na fila.
# As notificações locais funcionam via service worker.


async def get_user_push_subscriptions(user_id: str) -> List[dict]:
    """
    Obter todas as subscrições push activas de um utilizador.
    """
    subscriptions = await db.push_subscriptions.find(
        {"user_id": user_id, "is_active": True}
    ).to_list(10)
    
    return subscriptions


async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    icon: Optional[str] = "/logo192.png",
    badge: Optional[str] = "/logo192.png",
    tag: Optional[str] = None,
    url: Optional[str] = "/",
    data: Optional[dict] = None
) -> dict:
    """
    Enviar notificação push para um utilizador.
    
    Args:
        user_id: ID do utilizador
        title: Título da notificação
        body: Corpo da notificação
        icon: Ícone da notificação
        badge: Badge (ícone pequeno)
        tag: Tag para agrupar notificações
        url: URL para abrir ao clicar
        data: Dados adicionais
    
    Returns:
        Resultado do envio
    """
    subscriptions = await get_user_push_subscriptions(user_id)
    
    if not subscriptions:
        logger.info(f"Utilizador {user_id} não tem subscrições push activas")
        return {"success": False, "reason": "no_subscriptions"}
    
    payload = {
        "title": title,
        "body": body,
        "icon": icon,
        "badge": badge,
        "tag": tag or f"creditoimo-{datetime.now(timezone.utc).timestamp()}",
        "data": {
            "url": url,
            **(data or {})
        }
    }
    
    # Guardar na fila de notificações push (para processamento futuro com pywebpush)
    push_queue_item = {
        "user_id": user_id,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "subscription_count": len(subscriptions)
    }
    
    await db.push_notification_queue.insert_one(push_queue_item)
    
    logger.info(f"Notificação push enfileirada para {user_id} ({len(subscriptions)} subscrições)")
    
    # NOTA: Implementação completa com pywebpush:
    # from pywebpush import webpush, WebPushException
    # 
    # for sub in subscriptions:
    #     try:
    #         webpush(
    #             subscription_info={
    #                 "endpoint": sub["endpoint"],
    #                 "keys": sub["keys"]
    #             },
    #             data=json.dumps(payload),
    #             vapid_private_key=VAPID_PRIVATE_KEY,
    #             vapid_claims={"sub": "mailto:admin@creditoimo.pt"}
    #         )
    #     except WebPushException as e:
    #         logger.error(f"Erro ao enviar push: {e}")
    
    return {
        "success": True,
        "queued": True,
        "subscription_count": len(subscriptions)
    }


async def send_push_to_multiple_users(
    user_ids: List[str],
    title: str,
    body: str,
    **kwargs
) -> dict:
    """
    Enviar notificação push para múltiplos utilizadores.
    """
    results = {
        "total": len(user_ids),
        "sent": 0,
        "no_subscriptions": 0
    }
    
    for user_id in user_ids:
        result = await send_push_notification(user_id, title, body, **kwargs)
        if result.get("success"):
            results["sent"] += 1
        else:
            results["no_subscriptions"] += 1
    
    return results


async def cleanup_expired_subscriptions():
    """
    Remover subscrições expiradas.
    """
    # Marcar como inativas subscrições com expiration_time passado
    now = datetime.now(timezone.utc).timestamp() * 1000  # Em milliseconds
    
    result = await db.push_subscriptions.update_many(
        {
            "expiration_time": {"$ne": None, "$lt": now},
            "is_active": True
        },
        {"$set": {"is_active": False}}
    )
    
    if result.modified_count > 0:
        logger.info(f"Desactivadas {result.modified_count} subscrições push expiradas")
    
    return result.modified_count
