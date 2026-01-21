"""
Script para atribuir consultores/intermediários aos processos e adicionar eventos
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

EVENT_TYPES = [
    "Reunião com Cliente",
    "Entrega de Documentos",
    "Análise Bancária",
    "Avaliação de Imóvel",
    "Assinatura de Contrato",
    "Visita ao Imóvel",
    "Contacto Telefónico",
    "Envio de Proposta",
    "Aprovação Final",
    "Escritura"
]


async def setup_complete_data():
    """Atribui consultores/intermediários e cria eventos"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔗 Verificando ligações entre processos e staff...")
    
    # Obter consultores e intermediários
    consultores = await db.users.find({"role": {"$in": ["consultor", "consultor_intermediario"]}}).to_list(length=20)
    intermediarios = await db.users.find({"role": {"$in": ["intermediario", "consultor_intermediario"]}}).to_list(length=20)
    
    print(f"  • {len(consultores)} consultores disponíveis")
    print(f"  • {len(intermediarios)} intermediários disponíveis")
    
    # Processar processos
    processes = await db.processes.find({}).to_list(length=500)
    updated_processes = 0
    
    for process in processes:
        update_data = {}
        
        # Atribuir consultor se não tiver
        if not process.get('assigned_consultor') and consultores:
            consultor = random.choice(consultores)
            update_data['assigned_consultor'] = consultor['id']
            update_data['assigned_consultor_name'] = consultor['name']
        
        # Atribuir intermediário se não tiver
        if not process.get('assigned_intermediario') and intermediarios:
            intermediario = random.choice(intermediarios)
            update_data['assigned_intermediario'] = intermediario['id']
            update_data['assigned_intermediario_name'] = intermediario['name']
        
        if update_data:
            await db.processes.update_one(
                {"id": process["id"]},
                {"$set": update_data}
            )
            updated_processes += 1
    
    print(f"✅ {updated_processes} processos atualizados com atribuições")
    
    # Criar eventos para todos os utilizadores
    print("\n📅 Criando eventos no calendário...")
    
    all_staff = consultores + intermediarios
    all_processes = await db.processes.find({}).to_list(length=500)
    
    # Limpar deadlines antigos
    await db.deadlines.delete_many({})
    
    events_created = 0
    
    for user in all_staff:
        # Processos atribuídos a este usuário
        user_processes = [
            p for p in all_processes 
            if p.get('assigned_consultor') == user['id'] or p.get('assigned_intermediario') == user['id']
        ]
        
        # Criar 3-8 eventos para cada usuário
        num_events = random.randint(3, 8)
        
        for i in range(num_events):
            if not user_processes:
                continue
                
            process = random.choice(user_processes)
            
            # Data do evento (passado, presente ou futuro)
            days_offset = random.randint(-30, 60)
            event_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
            
            event_type = random.choice(EVENT_TYPES)
            
            # Status baseado na data
            if days_offset < -5:
                status = "completed"
            elif days_offset < 0:
                status = "overdue"
            else:
                status = "pending"
            
            deadline_doc = {
                "id": str(uuid.uuid4()),
                "process_id": process['id'],
                "title": f"{event_type} - {process['client_name']}",
                "description": f"{event_type} para o processo de {process['client_name']}",
                "due_date": event_date.strftime('%Y-%m-%d'),
                "status": status,
                "assigned_user_id": user['id'],
                "assigned_user_name": user['name'],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "priority": random.choice(["high", "medium", "low"])
            }
            
            await db.deadlines.insert_one(deadline_doc)
            events_created += 1
    
    print(f"✅ {events_created} eventos criados no calendário")
    
    # Estatísticas finais
    print("\n📊 Estatísticas Finais:")
    
    total_with_consultor = await db.processes.count_documents({"assigned_consultor": {"$ne": None}})
    total_with_intermediario = await db.processes.count_documents({"assigned_intermediario": {"$ne": None}})
    total_events = await db.deadlines.count_documents({})
    
    print(f"  • Processos com consultor: {total_with_consultor}")
    print(f"  • Processos com intermediário: {total_with_intermediario}")
    print(f"  • Total de eventos: {total_events}")
    
    # Eventos por status
    pending = await db.deadlines.count_documents({"status": "pending"})
    completed = await db.deadlines.count_documents({"status": "completed"})
    overdue = await db.deadlines.count_documents({"status": "overdue"})
    
    print(f"\n  Eventos por status:")
    print(f"    • Pendentes: {pending}")
    print(f"    • Concluídos: {completed}")
    print(f"    • Atrasados: {overdue}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(setup_complete_data())
