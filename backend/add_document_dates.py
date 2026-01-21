"""
Script para adicionar validades aleatórias de documentos aos processos
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Tipos de documentos comuns em processos imobiliários e crédito
DOCUMENT_TYPES = [
    "CC", "Cartão de Cidadão",
    "Título de Residência", 
    "IRS",
    "Recibos de Vencimento",
    "Declaração Segurança Social",
    "Certidão Permanente",
    "Caderneta Predial",
    "Escritura",
    "Contrato Promessa",
    "Certificado Energético",
    "Licença de Habitação",
    "Ficha Técnica Habitação"
]


async def add_document_expiries():
    """Adiciona datas de validade aleatórias aos documentos dos processos"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("📄 Adicionando datas de validade de documentos...")
    
    # Obter todos os processos
    processes = await db.processes.find({}).to_list(length=500)
    
    updated_count = 0
    
    for process in processes:
        # Criar alguns documentos com datas de validade para cada processo
        num_docs = random.randint(3, 8)
        selected_docs = random.sample(DOCUMENT_TYPES, num_docs)
        
        documents = []
        for doc_type in selected_docs:
            # Gerar datas de validade aleatórias
            # Alguns documentos já expiraram, outros estão para expirar, outros ainda válidos
            days_offset = random.choice([
                random.randint(-180, -30),  # Já expirados (30-180 dias atrás)
                random.randint(-30, 30),     # Prestes a expirar
                random.randint(30, 365),     # Válidos
            ])
            
            expiry_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
            
            documents.append({
                "type": doc_type,
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "status": "expired" if days_offset < 0 else ("expiring_soon" if days_offset < 30 else "valid")
            })
        
        # Atualizar processo
        await db.processes.update_one(
            {"id": process["id"]},
            {"$set": {"documents": documents}}
        )
        updated_count += 1
        
        if updated_count % 10 == 0:
            print(f"  ✓ {updated_count} processos atualizados...")
    
    print(f"\n✅ {updated_count} processos atualizados com datas de documentos!")
    
    # Estatísticas
    total_docs = sum([len(doc.get('documents', [])) for doc in await db.processes.find({}).to_list(length=500)])
    print(f"📊 Total de documentos adicionados: {total_docs}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(add_document_expiries())
