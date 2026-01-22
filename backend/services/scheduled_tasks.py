"""
====================================================================
TAREFAS AGENDADAS (CRON JOBS) - CREDITOIMO
====================================================================
Sistema de tarefas agendadas para execução diária.

Tarefas incluídas:
- Verificação de documentos a expirar
- Verificação de prazos a aproximar-se
- Limpeza de notificações antigas
- Geração de alertas automáticos

Uso:
    # Executar manualmente
    python -m services.scheduled_tasks
    
    # Ou via cron (Linux) - executar diariamente às 8h:
    0 8 * * * cd /app/backend && python -m services.scheduled_tasks
    
    # Ou iniciar como processo em background:
    python -m services.scheduled_tasks --daemon
====================================================================
"""

import asyncio
import logging
import argparse
from datetime import datetime, timezone, timedelta
from typing import List
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """Serviço de tarefas agendadas."""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
    
    async def connect(self):
        """Conectar à base de dados."""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info(f"Conectado à base de dados: {self.db_name}")
    
    async def disconnect(self):
        """Desconectar da base de dados."""
        if self.client:
            self.client.close()
            logger.info("Desconectado da base de dados")
    
    async def create_notification(
        self,
        user_id: str,
        message: str,
        notification_type: str,
        process_id: str = None,
        client_name: str = None,
        link: str = None
    ):
        """Criar uma notificação na base de dados."""
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "process_id": process_id,
            "client_name": client_name,
            "link": link,
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.notifications.insert_one(notification)
        return notification
    
    async def check_expiring_documents(self) -> int:
        """
        Verificar documentos a expirar nos próximos 7 dias.
        Criar notificações para os utilizadores responsáveis.
        """
        logger.info("A verificar documentos a expirar...")
        
        today = datetime.now(timezone.utc)
        warning_date = today + timedelta(days=7)
        
        # Buscar processos com documentos
        processes = await self.db.processes.find(
            {"documents": {"$exists": True, "$ne": []}},
            {"_id": 0}
        ).to_list(1000)
        
        notifications_created = 0
        
        for process in processes:
            documents = process.get("documents", [])
            
            for doc in documents:
                expiry_date_str = doc.get("expiry_date")
                if not expiry_date_str:
                    continue
                
                try:
                    expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
                except:
                    continue
                
                # Verificar se expira nos próximos 7 dias
                if today <= expiry_date <= warning_date:
                    days_until = (expiry_date - today).days
                    
                    # Notificar consultor e mediador
                    users_to_notify = []
                    if process.get("consultor_id"):
                        users_to_notify.append(process["consultor_id"])
                    if process.get("mediador_id"):
                        users_to_notify.append(process["mediador_id"])
                    
                    for user_id in users_to_notify:
                        # Verificar se já existe notificação similar recente
                        existing = await self.db.notifications.find_one({
                            "user_id": user_id,
                            "process_id": process.get("id"),
                            "type": "document_expiry",
                            "created_at": {"$gte": (today - timedelta(days=1)).isoformat()}
                        })
                        
                        if not existing:
                            await self.create_notification(
                                user_id=user_id,
                                message=f"Documento '{doc.get('name', 'Sem nome')}' expira em {days_until} dias",
                                notification_type="document_expiry",
                                process_id=process.get("id"),
                                client_name=process.get("client_name"),
                                link=f"/process/{process.get('id')}"
                            )
                            notifications_created += 1
        
        logger.info(f"Documentos a expirar: {notifications_created} notificações criadas")
        return notifications_created
    
    async def check_upcoming_deadlines(self) -> int:
        """
        Verificar prazos/eventos nas próximas 24 horas.
        Criar notificações para os participantes.
        """
        logger.info("A verificar prazos próximos...")
        
        today = datetime.now(timezone.utc)
        tomorrow = today + timedelta(days=1)
        
        # Buscar deadlines próximos
        deadlines = await self.db.deadlines.find({
            "date": {
                "$gte": today.isoformat(),
                "$lte": tomorrow.isoformat()
            }
        }, {"_id": 0}).to_list(500)
        
        notifications_created = 0
        
        for deadline in deadlines:
            participants = deadline.get("participants", [])
            
            for user_id in participants:
                # Verificar se já existe notificação similar
                existing = await self.db.notifications.find_one({
                    "user_id": user_id,
                    "type": "deadline_reminder",
                    "message": {"$regex": deadline.get("title", "")},
                    "created_at": {"$gte": (today - timedelta(hours=12)).isoformat()}
                })
                
                if not existing:
                    await self.create_notification(
                        user_id=user_id,
                        message=f"Lembrete: {deadline.get('title', 'Evento')} - amanhã",
                        notification_type="deadline_reminder",
                        process_id=deadline.get("process_id"),
                        link="/admin?tab=calendar"
                    )
                    notifications_created += 1
        
        logger.info(f"Prazos próximos: {notifications_created} notificações criadas")
        return notifications_created
    
    async def check_pre_approval_countdown(self) -> int:
        """
        Verificar processos com pré-aprovação a expirar (90 dias).
        Alertar quando faltam 30, 15, 7 e 3 dias.
        """
        logger.info("A verificar countdowns de pré-aprovação...")
        
        today = datetime.now(timezone.utc)
        alert_days = [30, 15, 7, 3]
        
        # Buscar processos com data de pré-aprovação
        processes = await self.db.processes.find({
            "credit_data.bank_approval_date": {"$exists": True, "$ne": None}
        }, {"_id": 0}).to_list(1000)
        
        notifications_created = 0
        
        for process in processes:
            approval_date_str = process.get("credit_data", {}).get("bank_approval_date")
            if not approval_date_str:
                continue
            
            try:
                approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
            except:
                continue
            
            # Calcular dias restantes (90 dias desde aprovação)
            expiry_date = approval_date + timedelta(days=90)
            days_remaining = (expiry_date - today).days
            
            if days_remaining in alert_days:
                users_to_notify = []
                if process.get("consultor_id"):
                    users_to_notify.append(process["consultor_id"])
                if process.get("mediador_id"):
                    users_to_notify.append(process["mediador_id"])
                
                for user_id in users_to_notify:
                    existing = await self.db.notifications.find_one({
                        "user_id": user_id,
                        "process_id": process.get("id"),
                        "type": "pre_approval_countdown",
                        "created_at": {"$gte": (today - timedelta(days=1)).isoformat()}
                    })
                    
                    if not existing:
                        await self.create_notification(
                            user_id=user_id,
                            message=f"⏰ Pré-aprovação expira em {days_remaining} dias!",
                            notification_type="pre_approval_countdown",
                            process_id=process.get("id"),
                            client_name=process.get("client_name"),
                            link=f"/process/{process.get('id')}"
                        )
                        notifications_created += 1
        
        logger.info(f"Countdown pré-aprovação: {notifications_created} notificações criadas")
        return notifications_created
    
    async def cleanup_old_notifications(self, days: int = 30) -> int:
        """
        Limpar notificações lidas com mais de X dias.
        """
        logger.info(f"A limpar notificações com mais de {days} dias...")
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        result = await self.db.notifications.delete_many({
            "read": True,
            "created_at": {"$lt": cutoff_date}
        })
        
        logger.info(f"Notificações removidas: {result.deleted_count}")
        return result.deleted_count
    
    async def run_all_tasks(self):
        """Executar todas as tarefas agendadas."""
        logger.info("=" * 50)
        logger.info("INICIANDO TAREFAS AGENDADAS")
        logger.info(f"Data/Hora: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 50)
        
        try:
            await self.connect()
            
            # Executar tarefas
            docs_count = await self.check_expiring_documents()
            deadlines_count = await self.check_upcoming_deadlines()
            countdown_count = await self.check_pre_approval_countdown()
            cleanup_count = await self.cleanup_old_notifications()
            
            logger.info("=" * 50)
            logger.info("RESUMO DAS TAREFAS")
            logger.info(f"- Alertas de documentos: {docs_count}")
            logger.info(f"- Alertas de prazos: {deadlines_count}")
            logger.info(f"- Alertas de countdown: {countdown_count}")
            logger.info(f"- Notificações limpas: {cleanup_count}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Erro nas tarefas agendadas: {e}")
            raise
        finally:
            await self.disconnect()


async def run_daemon(interval_hours: int = 24):
    """
    Executar tarefas em loop (modo daemon).
    Por defeito, executa a cada 24 horas.
    """
    service = ScheduledTasksService()
    
    while True:
        try:
            await service.run_all_tasks()
        except Exception as e:
            logger.error(f"Erro no daemon: {e}")
        
        # Aguardar próxima execução
        next_run = datetime.now() + timedelta(hours=interval_hours)
        logger.info(f"Próxima execução: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(interval_hours * 3600)


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='CreditoIMO - Tarefas Agendadas')
    parser.add_argument('--daemon', action='store_true', help='Executar em modo daemon (loop contínuo)')
    parser.add_argument('--interval', type=int, default=24, help='Intervalo em horas (para daemon)')
    
    args = parser.parse_args()
    
    if args.daemon:
        logger.info("Iniciando em modo daemon...")
        await run_daemon(args.interval)
    else:
        service = ScheduledTasksService()
        await service.run_all_tasks()


if __name__ == "__main__":
    asyncio.run(main())
