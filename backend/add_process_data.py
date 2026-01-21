"""
Script para adicionar dados aleatórios aos processos existentes
"""
import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

PROPERTY_TYPES = ["apartamento", "moradia", "terreno", "escritorio"]
LOCATIONS = [
    "Lisboa", "Porto", "Braga", "Coimbra", "Setúbal", "Faro", "Aveiro", "Viseu", 
    "Leiria", "Évora", "Cascais", "Oeiras", "Almada", "Matosinhos", "Vila Nova de Gaia",
    "Funchal", "Ponta Delgada", "Sintra", "Loures", "Amadora", "Odivelas", "Queluz",
    "Guimarães", "Barcelos", "Espinho", "Póvoa de Varzim", "Chaves", "Bragança"
]
SERVICE_TYPES = ["credito_habitacao", "refinanciamento", "compra_terreno", "investimento"]
PRIORITIES = ["high", "medium", "low"]


async def add_process_data():
    """Adiciona dados aleatórios aos processos"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("📝 Adicionando dados aos processos...")
    
    processes = await db.processes.find({}).to_list(length=500)
    updated_count = 0
    
    for process in processes:
        # Só adiciona se os dados não existirem
        update_data = {}
        
        if not process.get('property_type'):
            update_data['property_type'] = random.choice(PROPERTY_TYPES)
        
        if not process.get('property_location'):
            update_data['property_location'] = random.choice(LOCATIONS)
        
        if not process.get('service_type'):
            update_data['service_type'] = random.choice(SERVICE_TYPES)
        
        if not process.get('priority'):
            # Distribuição: 20% high, 50% medium, 30% low
            update_data['priority'] = random.choices(
                PRIORITIES, 
                weights=[20, 50, 30], 
                k=1
            )[0]
        
        # Se já tem property_value mas não tem loan_amount
        if process.get('property_value') and not process.get('loan_amount'):
            # Calcular loan_amount como 80-90% do property_value
            percentage = random.randint(80, 90) / 100
            update_data['loan_amount'] = int(process['property_value'] * percentage)
        
        # Se não tem property_value, gerar um
        if not process.get('property_value'):
            # Valores entre 100k e 800k
            property_value = random.randint(100, 800) * 1000
            update_data['property_value'] = property_value
            
            # E o loan_amount correspondente
            percentage = random.randint(80, 90) / 100
            update_data['loan_amount'] = int(property_value * percentage)
        
        # Se tem NIF vazio, gerar um
        if not process.get('client_nif'):
            update_data['client_nif'] = f"{random.randint(100000000, 999999999)}"
        
        if update_data:
            await db.processes.update_one(
                {"id": process["id"]},
                {"$set": update_data}
            )
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f"  ✓ {updated_count} processos atualizados...")
    
    print(f"\n✅ {updated_count} processos atualizados com dados!")
    
    # Estatísticas
    print("\n📊 Distribuição dos dados:")
    
    # Por tipo de imóvel
    print("\nPor tipo de imóvel:")
    for prop_type in PROPERTY_TYPES:
        count = await db.processes.count_documents({"property_type": prop_type})
        print(f"  • {prop_type.capitalize()}: {count}")
    
    # Por prioridade
    print("\nPor prioridade:")
    for priority in PRIORITIES:
        count = await db.processes.count_documents({"priority": priority})
        priority_label = {"high": "Alta", "medium": "Média", "low": "Baixa"}[priority]
        print(f"  • {priority_label}: {count}")
    
    # Por tipo de serviço
    print("\nPor tipo de serviço:")
    for service in SERVICE_TYPES:
        count = await db.processes.count_documents({"service_type": service})
        print(f"  • {service.replace('_', ' ').title()}: {count}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(add_process_data())
