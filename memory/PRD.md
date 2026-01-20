# CreditoIMO - Sistema de Registo de Clientes

## Problem Statement
Sistema de registo de clientes que podem precisar de crédito e de ajuda imobiliária ou as duas coisas. O cliente preenche os dados que depois podem ser alterados e adicionados campos pelo consultor ou pelo mediador. Alguns campos só podem ser preenchidos depois do processo ter autorização bancária. O processo tem de ter um calendário associado para saber os prazos.

## User Personas
1. **Cliente** - Cria processos, preenche dados pessoais e financeiros
2. **Consultor** - Gere dados imobiliários dos processos
3. **Mediador** - Gere dados de crédito (após autorização bancária)
4. **Admin** - Gestão de utilizadores e visualização completa

## Core Requirements (Static)
- Autenticação JWT com 4 roles
- Processos com fases: Pedido Inicial → Em Análise → Autorização Bancária → Aprovado/Rejeitado
- Dados pessoais e financeiros editáveis por cliente
- Dados imobiliários editáveis apenas por consultor
- Dados de crédito editáveis apenas por mediador (após autorização bancária)
- Calendário de prazos por processo
- Notificações por email (simuladas)

## Architecture
- **Backend**: FastAPI + MongoDB + JWT Auth
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Database**: MongoDB com collections: users, processes, deadlines, email_logs

## What's Been Implemented (2026-01-20)
- ✅ Sistema de autenticação completo (login/registo/JWT)
- ✅ 4 dashboards por role (Cliente, Consultor, Mediador, Admin)
- ✅ Criação de processos com wizard de 3 passos
- ✅ Formulários de dados pessoais, financeiros, imobiliários e crédito
- ✅ Sistema de prazos com calendário visual
- ✅ Gestão de utilizadores pelo admin
- ✅ Controle de acesso por role
- ✅ Notificações por email (simuladas/logs)
- ✅ Filtros e pesquisa nos dashboards

## Prioritized Backlog
### P0 (Crítico) - Done
- [x] Auth system
- [x] Process CRUD
- [x] Role-based access
- [x] Deadline management

### P1 (Importante)
- [ ] Notificações por email reais (integração SendGrid/Resend)
- [ ] Upload de documentos
- [ ] Histórico de alterações do processo
- [ ] Dashboard com gráficos de estatísticas

### P2 (Nice to Have)
- [ ] Notificações push
- [ ] Exportar processos para PDF
- [ ] Relatórios mensais
- [ ] Integração com bancos para verificação de crédito

## Next Tasks
1. Integrar serviço de email real (SendGrid ou Resend)
2. Sistema de upload de documentos
3. Auditoria/histórico de alterações

## Credentials (Dev)
- Admin: admin@sistema.pt / admin123
- Consultor: consultor@test.pt / test123
- Mediador: mediador@test.pt / test123
