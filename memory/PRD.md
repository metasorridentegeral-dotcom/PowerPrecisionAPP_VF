# CreditoIMO - Sistema de Registo de Clientes
## Power Real Estate & Precision

## Problem Statement
Sistema de registo de clientes para crédito e assistência imobiliária. Clientes preenchem formulário público (sem login). Consultores, mediadores e CEO gerem os processos num quadro Kanban visual estilo Trello.

## Sites de Referência
- **Imobiliária**: https://www.powerealestate.pt/
- **Crédito**: https://precision-credito.pt/

## User Roles (Hierarquia)
1. **Admin** - Gestão total do sistema, utilizadores e workflow
2. **CEO** - Vê todos os processos, pode fazer tudo que consultor e mediador fazem
3. **Consultor/Mediador** - Pode fazer tarefas de consultor E mediador
4. **Consultor** - Gere dados imobiliários, vê apenas os seus clientes atribuídos
5. **Mediador** - Gere dados de crédito, vê apenas os seus clientes atribuídos
6. **Cliente** - Preenche formulário público (sem login no sistema)

## What's Been Implemented

### ✅ Dados Importados do Trello (2026-01-20)
- **153 clientes** importados com todas as informações
- **14 fases** do workflow conforme Trello:
  1. Clientes em Espera
  2. Fase Documental
  3. Fase Documental II
  4. Enviado ao Bruno
  5. Enviado ao Luís
  6. Enviado BCP Rui
  7. Entradas Precision
  8. Fase Bancária - Pré Aprovação
  9. Fase de Visitas
  10. CH Aprovado - Avaliação
  11. Fase de Escritura
  12. Escritura Agendada
  13. Concluídos
  14. Desistências

### ✅ Utilizadores Criados
| Nome | Email | Role | Password |
|------|-------|------|----------|
| Pedro Borges | pedro@powerealestate.pt | CEO | power2026 |
| Tiago Borges | tiago@powerealestate.pt | Consultor | power2026 |
| Flávio da Silva | flavio@powerealestate.pt | Consultor | power2026 |
| Estácio Miranda | estacio@precisioncredito.pt | Mediador | power2026 |
| Fernando Andrade | fernando@precisioncredito.pt | Mediador | power2026 |
| Carina Amuedo | carina@powerealestate.pt | Consultor/Mediador | power2026 |
| Marisa Rodrigues | marisa@powerealestate.pt | Consultor/Mediador | power2026 |
| Admin | admin@sistema.pt | Admin | admin2026 |

### ✅ Quadro Kanban Visual (Estilo Trello)
- Colunas coloridas por fase
- Drag & drop para mover clientes entre fases
- Filtro automático por role:
  - Admin/CEO: Vê todos os 153 processos
  - Consultor: Vê apenas os seus (~50)
  - Mediador: Vê apenas os seus (~5)
- Cards mostram: nome, telefone, valor, prioridade, badges de atribuição
- Pesquisa por nome/email

### ✅ Email SMTP Funcional
- Servidor: mail.precisioncredito.pt:465 (SSL)
- Email de envio: admin@precisioncredito.pt
- Notificações automáticas quando cliente muda de fase

### ✅ Funcionalidades Anteriores
- Formulário público multi-step (6 passos)
- Sistema de prazos com calendário
- Histórico de alterações
- Sistema de comentários
- Análise AI de documentos (GPT-4o)
- Gestão de documentos a expirar

## Architecture
```
/app/backend/
├── server.py
├── models/auth.py (inclui UserRole com 6 roles)
├── routes/
│   ├── processes.py (/api/processes/kanban endpoint)
│   ├── stats.py (stats filtrados por role)
│   └── ...
└── services/
    └── email.py (SMTP SSL)

/app/frontend/
├── src/
│   ├── components/
│   │   └── KanbanBoard.js (componente Kanban)
│   └── pages/
│       └── StaffDashboard.js (dashboard unificado)
```

## URLs
- **Formulário Público**: / ou /registo
- **Login Staff**: /login
- **Dashboard Staff**: /staff (Kanban)
- **Dashboard Admin**: /admin

## Integrações
| Integração | Estado | Config |
|------------|--------|--------|
| SMTP Email | ✅ FUNCIONAL | mail.precisioncredito.pt:465 |
| GPT-4o (AI) | ✅ Preparado | EMERGENT_LLM_KEY |
| OneDrive | 🔴 Aguarda | Precisa Azure AD credentials |

## Próximas Tarefas
- [ ] CI/CD Pipeline para testes automatizados
- [ ] Integração OneDrive (aguarda credenciais Azure AD)
- [ ] Testar análise AI com documentos reais
