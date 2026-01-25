# CreditoIMO - Changelog

Registo de alterações do sistema CreditoIMO.

---

## [2026-01-25] - Sistema de Tarefas e Melhorias

### Adicionado
- **Sistema de Tarefas Completo**
  - CRUD completo via `/api/tasks`
  - Separador "Tarefas" no Admin Dashboard
  - Painel de tarefas na ficha do cliente
  - Atribuição a múltiplos utilizadores
  - Notificações automáticas quando tarefa atribuída
  - Prefixo automático `[Nome do Cliente]` quando criada da ficha

- **Alertas Automáticos**
  - Alerta para clientes em espera há 15+ dias (CEO/Diretor)
  - Lembrete mensal (1º dia) para pedir recibo e extrato
  - Email automático ao cliente para documentos mensais

### Alterado
- **Layout do Calendário**: Calendário mensal à esquerda, eventos à direita
- **Renomeado**: "Próximos Prazos" → "Próximos Eventos"

---

## [2026-01-24] - Push Notifications e WebSocket Fix

### Adicionado
- **Push Notifications com VAPID**
  - Endpoints `/api/notifications/push/subscribe`, `/unsubscribe`, `/status`
  - Biblioteca `pywebpush` para envio real de notificações
  - Service Worker para receber notificações (`sw-push.js`)
  - Componente de configuração em Definições > Notificações
  - Integração: push enviado quando utilizador não está online via WebSocket

### Corrigido
- **Bug WebSocket URL**: Corrigida construção da URL usando API `URL()`
- Resolvido erro `ws://localhost:443/ws` em ambiente de preview

---

## [2026-01-23] - Refatorização e Correções

### Adicionado
- **Funcionalidade Impersonate**
  - Admin pode "ver como" outro utilizador
  - Banner amarelo quando em modo impersonate
  - Auditoria registada

### Alterado
- **Refatorização AdminDashboard**
  - Reduzido de 1200 para 315 linhas (~74%)
  - Componentes modulares em `/components/admin/`

### Corrigido
- Endpoint `/api/admin/workflow-statuses` no frontend
- Imports em falta no `ProcessDetails.js`
- Endpoint `/api/auth/me` para campos de impersonate

### Removido
- Rotas não utilizadas (`/cliente`, `ClientDashboard.js`, etc.)

---

## [2026-01-22] - Alertas e Notificações

### Adicionado
- **Sistema de Alertas**
  - Alerta de idade (<35 anos) para Apoio ao Estado
  - Countdown de 90 dias após pré-aprovação
  - Alerta de documentos a expirar (15 dias antes)
  - Alerta de escritura automático no calendário

- **Notificações em Tempo Real**
  - WebSocket para notificações instantâneas
  - Som de notificação (ativável/desativável)
  - Badge de contagem não lidas no ícone

### Alterado
- Novos perfis: Diretor(a) e Administrativo(a)
- Checkbox "Menor de 35 anos" no formulário público
- Layout ProcessDetails: Atividade na sidebar direita

---

## [2026-01-20] - Importação Trello

### Adicionado
- 155 processos importados do Trello
- 14 fases de workflow configuradas
- Badge "Trello" nos cartões sincronizados

---

## [2026-01] - Lançamento Inicial

### Adicionado
- Quadro Kanban visual (estilo Trello)
- Formulário público de registo
- Sistema de login com roles (Admin, CEO, Diretor, Consultor, Intermediário)
- Gestão de processos de crédito imobiliário
- Email SMTP funcional
- Links OneDrive para documentos
- Editor de workflow
- CI/CD Pipeline com GitHub Actions
- Análise de documentos com IA (GPT-4o-mini)

---

## Legenda

- **Adicionado**: Novas funcionalidades
- **Alterado**: Alterações em funcionalidades existentes
- **Corrigido**: Correções de bugs
- **Removido**: Funcionalidades removidas
- **Segurança**: Alterações relacionadas com segurança
