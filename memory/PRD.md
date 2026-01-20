# CreditoIMO - Sistema de Registo de Clientes
## Power Real Estate & Precision

## Problem Statement
Sistema de registo de clientes que podem precisar de crédito e de ajuda imobiliária ou as duas coisas. O cliente preenche um formulário público inicial (sem login). O mediador e o consultor gerem depois o cliente.

## User Personas
1. **Cliente** - Preenche formulário público (sem login), recebe acompanhamento
2. **Consultor** - Gere dados imobiliários, altera estados, adiciona prazos
3. **Mediador** - Gere dados de crédito (após autorização bancária), altera estados
4. **Admin** - Gestão de utilizadores, gestão de fluxos de processos, configurações. Tem acesso a TODAS as funcionalidades de consultor e mediador

## Core Requirements
- Formulário público para clientes (sem autenticação)
- Autenticação JWT apenas para staff (consultor, mediador, admin)
- Processos com fases configuráveis pelo admin
- Histórico de alterações
- Sistema de comentários/atividade
- Integração OneDrive para documentos (preparado)
- Notificações por email (Resend - preparado)
- Análise AI de documentos (GPT-4o - preparado)

## Architecture
- **Backend**: FastAPI + MongoDB + JWT Auth
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Database**: MongoDB

### Backend Structure
```
/app/backend/
├── server.py          # Main app
├── config.py          # Configurações
├── database.py        # Conexão MongoDB
├── models/            # Pydantic models
├── routes/            # API endpoints
│   ├── auth.py        # /api/auth/*
│   ├── public.py      # /api/public/*
│   ├── processes.py   # /api/processes/*
│   ├── admin.py       # /api/users/*, /api/workflow-statuses/*
│   ├── deadlines.py   # /api/deadlines/* (com atribuições)
│   ├── activities.py  # /api/activities/*, /api/history
│   ├── documents.py   # /api/documents/*
│   ├── ai.py          # /api/ai/*
│   ├── onedrive.py    # /api/onedrive/*
│   └── stats.py       # /api/stats, /api/health
└── services/          # Business logic
    ├── auth.py        # JWT, password hashing
    ├── email.py       # Email notifications (Resend)
    ├── ai_document.py # GPT-4o document analysis
    ├── history.py     # Change logging
    └── onedrive.py    # OneDrive integration
```

## What's Been Implemented

### Fase 1-4 (Anteriores)
- ✅ Sistema de autenticação para staff
- ✅ 4 dashboards por role
- ✅ Sistema de prazos com calendário
- ✅ Histórico de alterações
- ✅ Sistema de comentários/atividade
- ✅ Gestão de estados de fluxo pelo admin
- ✅ Formulário público para clientes
- ✅ Backend refatorado para estrutura modular

### Fase 5 - Formulário Completo
- ✅ Formulário baseado na ficha de cliente PDF
- ✅ 6 passos: Dados Pessoais > 2º Titular > Imóvel > Situação Financeira > Créditos/Capital > Confirmação
- ✅ Mensagens de ajuda em todos os campos

### Fase 6 - Dashboard Admin Avançado
- ✅ Tabs: Visão Geral, Calendário, Documentos, Análise IA, Utilizadores, Fluxo, Configurações
- ✅ Calendário visual com filtros por consultor/mediador
- ✅ Estatísticas: Total Processos, Utilizadores, Prazos Pendentes, Estados

### Fase 7 - Melhorias (2026-01-20)
- ✅ **Removido estado "Autorização Bancária"** do workflow
- ✅ **Limpeza de utilizadores de teste** (30 eliminados)
- ✅ **Criar eventos no calendário com atribuição de consultor/mediador**
- ✅ **Admin tem acesso a todas funcionalidades** de consultor e mediador
- ✅ Dashboard do Consultor com análise AI
- ✅ Dashboard do Mediador com análise AI
- ✅ Documentos a expirar tracking

## Workflow Statuses (Atual)
| Ordem | Nome | Label |
|-------|------|-------|
| 1 | pedido_inicial | Pedido Inicial |
| 2 | em_analise | Em Análise |
| 4 | aprovado | Aprovado |
| 5 | rejeitado | Rejeitado |

## Credentials (Dev)
- **Admin**: admin@sistema.pt / admin123
- **Consultor**: consultor@sistema.pt / consultor123
- **Mediador**: mediador@sistema.pt / mediador123

## URLs
- **Formulário Público**: / ou /registo
- **Login Staff**: /login

## Integrações
| Integração | Estado | Notas |
|------------|--------|-------|
| Resend (Email) | MOCKED | RESEND_API_KEY vazio, emails simulados |
| OneDrive | MOCKED | Aguarda credenciais Azure AD |
| GPT-4o (AI) | Preparado | EMERGENT_LLM_KEY presente |

## Sites de Referência
- **Imobiliária**: https://www.powerealestate.pt/
- **Crédito**: https://precision-credito.pt/

## Próximas Tarefas
- [ ] Configurar Resend API key para emails reais
- [ ] Configurar OneDrive com credenciais Azure AD
- [ ] Testar análise AI de documentos
- [ ] CI/CD pipeline para testes automatizados
