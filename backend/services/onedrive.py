import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException
from config import ONEDRIVE_TENANT_ID, ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET
from models.onedrive import OneDriveFile

logger = logging.getLogger(__name__)

class OneDriveService:
    def __init__(self):
        self.token = None
        self.token_expires = None
    
    async def get_access_token(self) -> str:
        if not all([ONEDRIVE_TENANT_ID, ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET]):
            logger.error("Credenciais Azure não configuradas no .env")
            return None
        
        if self.token and self.token_expires and datetime.now(timezone.utc) < self.token_expires:
            return self.token
        
        token_url = f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}/oauth2/v2.0/token"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data={
                    "client_id": ONEDRIVE_CLIENT_ID,
                    "client_secret": ONEDRIVE_CLIENT_SECRET,
                    "scope": "https://graph.microsoft.com/.default",
                    "grant_type": "client_credentials"
                })
                response.raise_for_status()
                data = response.json()
                self.token = data["access_token"]
                self.token_expires = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"] - 60)
                return self.token
        except Exception as e:
            logger.error(f"Erro autenticação Azure: {e}")
            return None

    async def create_client_folder(self, client_name: str):
        token = await self.get_access_token()
        if not token: return None

        # 1. Criar Pasta
        folder_url = f"https://graph.microsoft.com/v1.0/users/geral@powerealestate.pt/drive/root:/Clientes/2026/{client_name}:/children"
        # NOTA: Substitui 'geral@powerealestate.pt' pelo ID do utilizador se der erro, mas o email costuma funcionar
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        body = {"name": client_name, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}

        try:
            async with httpx.AsyncClient() as client:
                # Tenta criar na raiz ou caminho especifico
                create_url = f"https://graph.microsoft.com/v1.0/users/geral@powerealestate.pt/drive/root:/Clientes/2026/{client_name}"
                # Método simplificado: PUT para criar/obter
                response = await client.put(
                    f"https://graph.microsoft.com/v1.0/users/geral@powerealestate.pt/drive/root:/Clientes/2026/{client_name}:/content", 
                    headers=headers
                )
                
                # A Graph API é complexa para "App Permissions". 
                # Se isto for complicado, O Power Automate (pago) é mais simples de configurar.
                return None 
        except Exception as e:
            logger.error(f"Erro OneDrive Azure: {e}")
            return None

    # Manter métodos vazios para compatibilidade
    async def list_files(self, path): return []
    async def get_download_url(self, id): return None

onedrive_service = OneDriveService()