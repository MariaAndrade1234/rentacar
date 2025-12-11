# Authentication API Documentation

## Overview
Sistema completo de autenticação para o RentACar com gerenciamento de tokens, histórico de login e recuperação de senha.

## Recursos
- ✅ Registro de usuários
- ✅ Login/Logout
- ✅ Tokens de autenticação customizados
- ✅ Refresh tokens
- ✅ Alteração de senha
- ✅ Recuperação de senha via email
- ✅ Histórico de login
- ✅ Rastreamento de dispositivos e IPs

## Endpoints

### Autenticação

#### **POST** `/api/auth/register/`
Registrar novo usuário.

**Request:**
```json
{
  "username": "joao",
  "email": "joao@example.com",
  "password": "SenhaSegura123",
  "confirm_password": "SenhaSegura123",
  "first_name": "João",
  "last_name": "Silva"
}
```

**Response:** `201 Created`
```json
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "username": "joao",
    "email": "joao@example.com",
    "first_name": "João",
    "last_name": "Silva",
    "is_active": true,
    "date_joined": "2025-12-09T10:00:00Z"
  }
}
```

#### **POST** `/api/auth/login/`
Fazer login.

**Request:**
```json
{
  "username": "joao",
  "password": "SenhaSegura123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "joao",
    "email": "joao@example.com",
    "first_name": "João",
    "last_name": "Silva"
  },
  "token": "abc123xyz...",
  "refresh_token": "xyz789abc...",
  "expires_at": "2025-12-10T10:00:00Z"
}
```

#### **POST** `/api/auth/logout/`
Fazer logout (requer autenticação).

**Headers:**
```
Authorization: Bearer abc123xyz...
```

**Response:** `200 OK`
```json
{
  "message": "Logout successful"
}
```

#### **POST** `/api/auth/token/refresh/`
Renovar token de autenticação.

**Request:**
```json
{
  "refresh_token": "xyz789abc..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Token refreshed successfully",
  "token": "new_token_here...",
  "refresh_token": "new_refresh_token...",
  "expires_at": "2025-12-10T10:00:00Z"
}
```

### Gerenciamento de Senha

#### **POST** `/api/auth/password/change/`
Alterar senha (requer autenticação).

**Headers:**
```
Authorization: Bearer abc123xyz...
```

**Request:**
```json
{
  "old_password": "SenhaAntiga123",
  "new_password": "SenhaNova456",
  "confirm_password": "SenhaNova456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

#### **POST** `/api/auth/password/reset/`
Solicitar recuperação de senha.

**Request:**
```json
{
  "email": "joao@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "If your email is registered, you will receive a password reset link"
}
```

#### **POST** `/api/auth/password/reset/confirm/`
Confirmar nova senha com token.

**Request:**
```json
{
  "token": "reset_token_here...",
  "new_password": "NovaSenha789",
  "confirm_password": "NovaSenha789"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset successful"
}
```

### Histórico

#### **GET** `/api/auth/history/`
Ver histórico de logins (requer autenticação).

**Headers:**
```
Authorization: Bearer abc123xyz...
```

**Response:** `200 OK`
```json
{
  "login_history": [
    {
      "id": 1,
      "username": "joao",
      "login_time": "2025-12-09T10:00:00Z",
      "logout_time": null,
      "ip_address": "192.168.1.1",
      "device_info": "Mozilla/5.0...",
      "success": true,
      "failure_reason": null
    }
  ]
}
```

## Models

### AuthToken
- Tokens customizados de autenticação
- Refresh tokens
- Rastreamento de dispositivo e IP
- Expiração configurável (24h access, 30 dias refresh)

### PasswordResetToken
- Tokens de recuperação de senha
- Expiração de 1 hora
- Uso único

### LoginHistory
- Histórico completo de logins
- Tentativas bem-sucedidas e falhas
- Informações de dispositivo e IP

## Segurança

- Senhas hash com algoritmo do Django
- Tokens únicos gerados com `secrets`
- Validação de força de senha
- Proteção contra enumeração de email
- Rastreamento de tentativas de login
- Revogação automática de tokens expirados

## Comandos de Gerenciamento

```bash
# Limpar tokens expirados
python manage.py cleanup_tokens

# Limpar tokens expirados (dry run)
python manage.py cleanup_tokens --dry-run
```

## Configuração

Adicione ao `MIDDLEWARE` em `settings.py`:
```python
MIDDLEWARE = [
    # ...
    'auth.middleware.TokenAuthenticationMiddleware',
]
```

Adicione ao `AUTHENTICATION_BACKENDS`:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'auth.backends.TokenAuthenticationBackend',
]
```
