# RentACar API

Sistema completo de aluguel de carros desenvolvido com Django REST Framework, seguindo padrões do projeto Alexandria.

## Recursos Implementados

### Autenticação (`/api/auth/`)
- ✅ Registro de usuários com validação
- ✅ Login/Logout
- ✅ Tokens customizados (access + refresh)
- ✅ Alteração de senha
- ✅ Recuperação de senha via token
- ✅ Histórico de login com rastreamento
- ✅ Rastreamento de dispositivos e IPs
- ✅ Middleware de autenticação customizado

### Contas (`/api/accounts/`)
- ✅ Gerenciamento de perfis de usuário
- ✅ Validações customizadas (email, username, senha)
- ✅ Serializers REST completos
- ✅ Camada de serviços

### Aluguéis (`/api/rentals/`)
- ✅ Criar/gerenciar aluguéis de carros
- ✅ Verificação de disponibilidade de veículos
- ✅ Cálculo automático de preços
- ✅ Validação de datas e períodos
- ✅ Status de aluguel (pending, confirmed, active, completed, cancelled, delayed)
- ✅ Serviços adicionais (seguro, GPS, cadeira infantil, etc)

##  Instalação

### Windows PowerShell

```powershell
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente (criar arquivo .env)
# SECRET_KEY=sua-chave-secreta-aqui
# DEBUG=True

# 4. Executar migrações
python manage.py makemigrations
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Executar servidor
python manage.py runserver 127.0.0.1:8000

# Após iniciar, acesse: http://127.0.0.1:8000/api/
```

## Comandos Úteis

```bash
# Limpar tokens expirados
python manage.py cleanup_tokens

# Limpar tokens expirados (dry run)
python manage.py cleanup_tokens --dry-run

# Executar testes
python manage.py test

# Executar testes de um app específico
python manage.py test auth

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas inspirada no Alexandria API:

1. **Views** - Endpoints da API (REST)
2. **Serializers** - Validação e serialização de dados
3. **Services** - Lógica de negócio separada
4. **Models** - Camada de dados
5. **Validations** - Validações customizadas
6. **Types** - Definições de tipos (TypedDict)
7. **Docs** - Documentação por app

## 🔐 Autenticação

### Endpoints Principais

```bash
POST /api/auth/register/      # Registrar usuário
POST /api/auth/login/         # Login
POST /api/auth/logout/        # Logout
POST /api/auth/token/refresh/ # Renovar token
POST /api/auth/password/change/        # Alterar senha
POST /api/auth/password/reset/         # Solicitar reset
POST /api/auth/password/reset/confirm/ # Confirmar reset
GET  /api/auth/history/       # Histórico de logins
```

### Exemplo de Uso

```bash
# 1. Registrar
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "email": "joao@example.com",
    "password": "SenhaSegura123",
    "confirm_password": "SenhaSegura123"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "password": "SenhaSegura123"
  }'

# Resposta:
# {
#   "token": "abc123...",
#   "refresh_token": "xyz789...",
#   "expires_at": "2025-12-10T10:00:00Z"
# }

# 3. Usar token nas requisições
curl -X GET http://localhost:8000/api/auth/history/ \
  -H "Authorization: Bearer abc123..."
```

## Testes

O projeto possui testes completos para todos os módulos:

```bash
# Executar todos os testes
python manage.py test

# Executar testes do auth
python manage.py test auth

# Executar com verbosidade
python manage.py test --verbosity=2
```

## Status do Projeto ✅

- ✅ Arquitetura completa (Alexandria API pattern)
- ✅ Autenticação com tokens customizados
- ✅ 4 Apps funcionais (authentication, accounts, cars, rentals)
- ✅ 9 modelos de banco de dados
- ✅ Service layer com lógica de negócio
- ✅ 55 testes passando (100% sucesso)
- ✅ Admin customizado
- ✅ Documentação completa

## Próximos Passos (Opcional)

- [ ] Frontend em React/Vue
- [ ] Integração de pagamento (Stripe/PayPal)
- [ ] Notificações por email
- [ ] SMS alerts
- [ ] Dashboard analítico
- [ ] Mobile app (React Native)

## API Endpoints Disponíveis

```
GET  /admin/                  - Admin do Django
POST /api/auth/register/      - Registrar usuário
POST /api/auth/login/         - Login
POST /api/auth/logout/        - Logout  
GET  /api/accounts/           - Listar contas
GET  /api/cars/               - Listar carros
POST /api/cars/               - Criar carro
GET  /api/rentals/            - Listar aluguéis
POST /api/rentals/            - Criar aluguel
```
