"""
Script para importar dados do Trello para o MongoDB
"""
import asyncio
import json
import uuid
import re
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# Configuração do MongoDB
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Mapeamento de listas do Trello para workflow statuses
TRELLO_LIST_MAPPING = {
    "677fddba997697a04140e50f": "clientes_espera",          # Clientes em espera
    "677fddba997697a04140e50e": "fase_documental",           # Fase Documental
    "686cf449a0725b747d61ef53": "fase_documental_ii",        # Fase Documental II
    "688203764c854e55b72e28b5": "enviado_bruno",             # Enviado ao Bruno
    "686d2301e1733e4b24429a91": "enviado_luis",              # Enviado ao Luís
    "68d2b2c3acc956a338b9eede": "enviado_bcp_rui",           # Enviado BCP Rui
    "686ced9e09f52ef2fbbfccac": "entradas_precision",        # Entradas Precision
    "677fddba997697a04140e510": "fase_bancaria",             # Fase Bancária - Pré Aprovação
    "677fddba997697a04140e512": "fase_visitas",              # Fase de visitas
    "677fddba997697a04140e511": "ch_aprovado",               # CH Aprovado - Avaliação
    "677fdf4207922a7ed8551c74": "fase_escritura",            # Fase de escritura
    "686cf61ca619cee471c6af13": "escritura_agendada",        # Escritura agendada
    "679e77e4d9e359dcb47fbba6": "concluidos",                # Concluidos
    "686ce75e8f9280a46cb4e62c": "desistencias",              # Desistências
}

# Mapeamento de membros do Trello para usuários do sistema
TRELLO_MEMBER_MAPPING = {
    "677fda465350a2750434eb57": "pedro@powerealestate.pt",      # Pedro Borges
    "677ff4792020f37416f4a286": "tiago@powerealestate.pt",      # Tiago Borges
    "677eaaf8803daac4eccb427a": "flavio@powerealestate.pt",     # Flávio da Silva
    "6945d81d1ea78c8a01063b31": "estacio@precisioncredito.pt",  # Estácio Miranda
    "694edf774a1af23b88de37eb": "fernando@precisioncredito.pt", # Fernando Andrade
    "695ba944ddc8963044b21735": "carina@powerealestate.pt",     # Carina Amuedo
    "686cdf233ffbef2763609334": "marisa@powerealestate.pt",     # Marisa Rodrigues
}


def extract_phone(text):
    """Extrai número de telefone do texto"""
    if not text:
        return None
    # Procurar padrões de telefone português
    patterns = [
        r'\+351\s*\d{3}\s*\d{3}\s*\d{3}',
        r'\d{9}',
        r'\d{3}\s*\d{3}\s*\d{3}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(0).strip()
            # Normalizar formato
            phone = re.sub(r'\s+', ' ', phone)
            if not phone.startswith('+351'):
                phone = '+351 ' + phone.replace(' ', '')
                phone = '+351 ' + phone[5:8] + ' ' + phone[8:11] + ' ' + phone[11:]
            return phone.strip()
    return None


def extract_email(text):
    """Extrai email do texto"""
    if not text:
        return None
    # Procurar padrão de email
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if match:
        return match.group(0).strip().lower()
    return None


def extract_value(text, keywords=['financiad', 'valor', 'compra', '€']):
    """Extrai valor monetário do texto"""
    if not text:
        return None
    
    # Procurar valores como "250.000€" ou "250k" ou "250.000"
    patterns = [
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€',
        r'(\d{1,3})\.(\d{3})k?',
        r'(\d{1,3})k',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Pegar o primeiro valor numérico mais alto encontrado
            values = []
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        # Para padrão com grupos
                        if len(match) == 2 and match[1]:
                            value = int(match[0]) * 1000 + int(match[1])
                        else:
                            # Limpar e converter
                            clean_match = match[0].replace('.', '').replace(',', '') if isinstance(match[0], str) else str(match[0])
                            value = int(clean_match)
                    else:
                        # Para padrão simples - limpar primeiro
                        clean_match = str(match).replace('.', '').replace(',', '').replace('€', '').strip()
                        if 'k' in clean_match.lower():
                            value = int(clean_match.lower().replace('k', '')) * 1000
                        else:
                            value = int(clean_match) if clean_match.isdigit() else int(clean_match) * 1000
                    values.append(value)
                except (ValueError, AttributeError):
                    continue
            
            if values:
                return max(values)  # Retornar o maior valor (geralmente o valor do imóvel)
    
    return None


def parse_client_name(card_name):
    """Extrai nome do cliente do título do card"""
    # Remover informações extras como valores e tipos
    name = re.sub(r'\s*[-/]\s*(CH|Ref|Refi|HS|100%|80%).*', '', card_name, flags=re.IGNORECASE)
    name = re.sub(r'\s*[-€]\s*\d+.*', '', name)
    return name.strip()


async def import_trello_data(json_file_path):
    """Importa dados do ficheiro JSON do Trello"""
    
    # Carregar dados do JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        trello_data = json.load(f)
    
    print(f"📥 Importando dados do Trello: {trello_data.get('name')}")
    
    # Conectar ao MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Criar mapeamento de membros (Trello ID -> MongoDB User ID)
    member_id_map = {}
    for trello_id, email in TRELLO_MEMBER_MAPPING.items():
        user = await db.users.find_one({"email": email})
        if user:
            member_id_map[trello_id] = user["id"]
            print(f"  ✓ Mapeado: {email} -> {user['name']}")
    
    # Processar cards
    cards = trello_data.get('cards', [])
    imported = 0
    skipped = 0
    
    print(f"\n📋 Processando {len(cards)} cards...")
    
    for card in cards:
        # Ignorar cards fechados ou cards de exemplo/dicas
        if card.get('closed', False):
            continue
        
        card_name = card.get('name', '')
        if 'Dica do Trello' in card_name or not card_name.strip():
            skipped += 1
            continue
        
        # Obter lista (status)
        trello_list_id = card.get('idList')
        status = TRELLO_LIST_MAPPING.get(trello_list_id)
        
        if not status:
            print(f"  ⚠ Lista não mapeada para card: {card_name}")
            skipped += 1
            continue
        
        # Extrair informações do cliente
        client_name = parse_client_name(card_name)
        desc = card.get('desc', '')
        
        # Extrair dados da descrição
        phone = extract_phone(desc) or extract_phone(card_name)
        email = extract_email(desc)
        property_value = extract_value(desc) or extract_value(card_name)
        
        # Verificar se já existe
        if email:
            existing = await db.processes.find_one({"client_email": email})
            if existing:
                skipped += 1
                continue
        
        # Obter membros atribuídos
        assigned_members = card.get('idMembers', [])
        assigned_consultor = None
        assigned_intermediario = None
        
        for member_id in assigned_members:
            if member_id in member_id_map:
                user_id = member_id_map[member_id]
                user = await db.users.find_one({"id": user_id})
                if user:
                    role = user.get('role')
                    if role in ['consultor', 'consultor_intermediario'] and not assigned_consultor:
                        assigned_consultor = user_id
                    if role in ['intermediario', 'consultor_intermediario'] and not assigned_intermediario:
                        assigned_intermediario = user_id
        
        # Criar processo
        process_doc = {
            "id": str(uuid.uuid4()),
            "client_name": client_name,
            "client_email": email or f"{client_name.lower().replace(' ', '.')}@trello.import",
            "client_phone": phone,
            "client_nif": None,
            "status": status,
            "service_type": "credito_habitacao",
            "property_type": None,
            "property_location": None,
            "property_value": property_value,
            "loan_amount": int(property_value * 0.85) if property_value else None,
            "priority": "medium",
            "assigned_consultor": assigned_consultor,
            "assigned_intermediario": assigned_intermediario,
            "notes": desc[:500] if desc else f"Importado do Trello - {card_name}",
            "tags": ["trello", "importado"],
            "trello_card_id": card.get('id'),
            "trello_url": card.get('shortUrl'),
            "created_at": card.get('dateLastActivity', datetime.now(timezone.utc).isoformat()),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await db.processes.insert_one(process_doc)
            imported += 1
            
            if imported % 10 == 0:
                print(f"  ✓ {imported} processos importados...")
        except Exception as e:
            print(f"  ✗ Erro ao importar {client_name}: {e}")
            skipped += 1
    
    print(f"\n✅ Importação concluída!")
    print(f"  • Importados: {imported}")
    print(f"  • Ignorados: {skipped}")
    
    # Estatísticas finais
    total_processes = await db.processes.count_documents({})
    print(f"\n📊 Total de processos no sistema: {total_processes}")
    
    # Distribuição por fase
    print("\n📈 Distribuição por fase:")
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    async for result in db.processes.aggregate(pipeline):
        status_name = result['_id']
        count = result['count']
        status_doc = await db.workflow_statuses.find_one({"name": status_name})
        label = status_doc.get('label', status_name) if status_doc else status_name
        print(f"  • {label}: {count} processos")
    
    client.close()


if __name__ == "__main__":
    import sys
    json_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/clientes.json'
    asyncio.run(import_trello_data(json_file))
