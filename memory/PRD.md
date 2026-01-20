# CreditoIMO - Sistema de Registo de Clientes

## Problem Statement
Sistema de registo de clientes que podem precisar de crédito e de ajuda imobiliária ou as duas coisas. O cliente preenche um formulário público inicial (sem login). O mediador e o consultor gerem depois o cliente.

## User Personas
1. **Cliente** - Preenche formulário público (sem login), recebe acompanhamento
2. **Consultor** - Gere dados imobiliários, altera estados, adiciona prazos
3. **Mediador** - Gere dados de crédito (após autorização bancária), altera estados
4. **Admin** - Gestão de utilizadores, gestão de fluxos de processos, configurações

## Core Requirements
- Formulário público para clientes (sem autenticação)
- Autenticação JWT apenas para staff (consultor, mediador, admin)
- Processos com fases configuráveis pelo admin
- Histórico de alterações
- Sistema de comentários/atividade
- Integração OneDrive para documentos (preparado)
- Notificações por email (simuladas)

## Architecture
- **Backend**: FastAPI + MongoDB + JWT Auth
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Database**: MongoDB

## What's Been Implemented

### Fase 1 (2026-01-20)
- ✅ Sistema de autenticação para staff
- ✅ 4 dashboards por role
- ✅ Sistema de prazos com calendário

### Fase 2 (2026-01-20)
- ✅ Histórico de alterações
- ✅ Sistema de comentários/atividade
- ✅ Gestão de estados de fluxo pelo admin
- ✅ Integração OneDrive preparada

### Fase 3 (2026-01-20)
- ✅ Formulário público para clientes (sem login)
- ✅ Processos de simulação criados
- ✅ Fluxo completo: cliente regista-se → consultor/mediador gerem

## Processos de Simulação
| Cliente | Tipo | Estado |
|---------|------|--------|
| António Ferreira | Crédito | Pedido Inicial |
| Carla Rodrigues | Imobiliária | Pedido Inicial |
| Rui Mendes | Crédito + Imobiliária | Autorização Bancária |
| Sofia Almeida | Crédito | Pedido Inicial |

## Integrações Pendentes
- [ ] OneDrive (requer credenciais Azure AD)
- [ ] HCPRO (dados imobiliários) - para futuro
- [ ] CRMCREDITO (dados de crédito) - para futuro

## Credentials (Dev)
- **Admin**: admin@sistema.pt / admin123
- **Consultor**: consultor@sistema.pt / consultor123
- **Mediador**: mediador@sistema.pt / mediador123

## URLs
- **Formulário Público**: / ou /registo
- **Login Staff**: /login

## MOCKED APIs
- **Email**: Notificações simuladas (logs)
- **OneDrive**: Preparado, não configurado
