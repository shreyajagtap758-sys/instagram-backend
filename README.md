# 📱 Instagram Backend - Scalable & Reliable System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7%2B-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**A production-ready backend system designed for Instagram-like social media platform with enterprise-grade security, scalability, and reliability.**

[Features](#features) • [Architecture](#architecture) • [API Endpoints](#api-endpoints) • [Setup](#setup) • [Security](#security)

</div>

---

## 🎯 Overview

This is a **scalable and reliable backend system** for an Instagram clone built with cutting-edge technologies. It implements industry best practices for authentication, data persistence, caching, and error handling.

### Key Highlights
- ⚡ **Async-First Architecture** - FastAPI for high throughput
- 🔐 **Enterprise Security** - JWT tokens, MFA (TOTP), brute-force protection
- 💾 **Smart Caching** - Redis token management and sessions
- 📊 **Scalable Database** - PostgreSQL with optimized indexes
- 🛡️ **Comprehensive Error Handling** - Custom exceptions with structured responses
- 📝 **Cursor-Based Pagination** - Efficient data retrieval for large datasets

---

## 🏗️ Architecture

### Directory Structure

```
instagram-backend/
├── server/
│   └── src/
│       ├── core/                          # Core configurations & infrastructure
│       │   ├── config.py                  # Settings management
│       │   ├── email_config.py            # Email service configuration
│       │   ├── redis.py                   # Redis client
│       │   ├── db/database.py             # Database setup
│       │   ├── keys/                      # JWT keys (private/public)
│       │   └── AuthSecurity/              # Security utilities
│       │
│       ├── models/                        # Database schemas (ORM)
│       │   ├── users.py                   # User entity
│       │   ├── posts.py                   # Post/media entity
│       │   ├── follow.py                  # Follow relationships
│       │   ├── mfauth.py                  # Multi-factor authentication
│       │   ├── password_reset.py          # Password reset tokens
│       │   └── refresh.py                 # Refresh token management
│       │
│       ├── schemas/                       # Pydantic request/response models
│       │   ├── user.py                    # User DTOs
│       │   ├── password.py                # Password schemas
│       │   └── follow.py                  # Follow schemas
│       │
│       ├── routes/                        # API endpoints
│       │   ├── user.py                    # Auth endpoints
│       │   ├── password.py                # Password endpoints
│       │   └── follow.py                  # Follow endpoints
│       │
│       ├── services/                      # Business logic
│       │   ├── users.py                   # User operations
│       │   ├── password.py                # Password operations
│       │   ├── follow.py                  # Follow operations
│       │   └── tokens.py                  # Token management
│       │
│       ├── repository/                    # Data access layer
│       │   ├── user.py                    # User queries
│       │   ├── password.py                # Password reset queries
│       │   ├── follow.py                  # Follow queries
│       │   ├── token.py                   # Token operations
│       │   └── redis.py                   # Redis operations
│       │
│       ├── error_handling/                # Error management
│       │   ├── base.py                    # Base exception
│       │   ├── handlers.py                # Exception handlers
│       │   └── exceptions/                # Custom exceptions
│       │
│       └── utils/                         # Utilities
│           ├── dependency.py              # FastAPI dependencies
│           ├── tokens.py                  # Token utilities
│           └── validations.py             # Input validation
```

---

# ✨ Features

## 1. 👤 User Authentication & Management ✅

### Features:

- User registration with email/username validation
- Secure login with JWT token generation
- Password hashing with Bcrypt (12 rounds)
- Brute-force protection (5 attempts → 15 min lock)
- Session management with access & refresh tokens
- Logout with token blacklisting

### Database Schema:

**Users Table**
```sql
- id: UUID (Primary Key)
- email: String (Unique, Indexed)
- username: String (Unique, Indexed)
- hashed_password: String
- is_locked: Boolean (brute-force protection)
- lock_until: DateTime (auto-unlock)
- failed_login_attempts: Integer
- last_login: DateTime
- follower_count: Integer (denormalized)
- following_count: Integer (denormalized)
- status: String ('active' | 'suspended')
- created_at: DateTime
- updated_at: DateTime
```

## 2. 🔐 Security & Authentication ✅

### JWT Tokens (RS256)

- Algorithm: RSA Signature with SHA-256
- Access Token: 15-minute expiration
- Refresh Token: 7-day expiration
- Token Claims: sub, exp, jti

### Password Security

- Algorithm: Bcrypt
- Rounds: 12

**Requirements:**
- ✓ Minimum 8 characters
- ✓ At least 1 uppercase (A-Z)
- ✓ At least 1 digit (0-9)
- ✓ At least 1 special character (!@#$%^&*)

### Token Blacklisting

- Implementation: Redis
- Instant revocation on logout
- TTL matching token expiration
- Auto-cleanup after expiration
- Sub-millisecond lookup

### Brute-Force Protection

- Mechanism: Account locking
- Max Attempts: 5
- Lock Duration: 15 minutes
- Auto-unlock: After 15 minutes
- Counter Reset: On successful login

## 3. 👥 Follow System ✅

### Features

- Follow/unfollow users
- Prevent self-follow (database constraint)
- Prevent duplicate follows (unique constraint)
- Paginated followers & following lists
- Cursor-based pagination for scalability


#### Database Schema:

**Follow Table**
```sql
- id: UUID
- follower_id: UUID (Foreign Key)
- following_id: UUID (Foreign Key)
- status: String ('active' | 'blocked' | 'pending')
- is_muted: Boolean
- created_at: DateTime
- deleted_at: DateTime (soft-delete)

Constraints:
✓ UNIQUE: (follower_id, following_id)
✓ CHECK: follower_id != following_id
✓ CASCADE DELETE: on user deletion
```

## 4. 🔑 Password Management ✅

## Features:
- Change password (requires current password)
- Forgot password (email-based reset)
- Reset password with token validation
- One-time token consumption (prevents replay)
- 24-hour expiration

### Password Reset Flow

1. User requests reset → Generate secure token
2. Send email with reset link
3. User clicks link → Validate token
4. Submit new password → Validate strength
5. Update password → Invalidate all tokens
6. Force re-authentication

---

# 🔌 API Endpoints

## 🔐 Authentication (`/user`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/user/signup` | Create a new account | ❌ |
| `POST` | `/user/login` | Authenticate user & receive tokens | ❌ |
| `GET` | `/user/me` | Retrieve current user profile | ✅ |
| `POST` | `/user/get_access_token`| Refresh expired access token | ❌ |
| `POST` | `/user/logout` | End session & blacklist token | ✅ |

## 🔑 Password Management (`/password`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/password/change-password` | Change password | ✅ |
| `POST` | `/password/forgot-password` | Request password reset | ❌ |
| `POST` | `/password/reset-password` | Reset password | ❌ |

## 👥 Social & Follow (`/follow`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/follow/{user_id}` | Follow a user | ✅ |
| `DELETE` | `/follow/{user_id}` | Unfollow a user | ✅ |
| `GET` | `/follow/followers/{user_id}`| Get followers list | ✅ |
| `GET` | `/follow/following/{user_id}`| Get following list | ✅ |


## 📋 Request/Response Examples

### POST /user/signup
```
Request:
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response (201):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

### POST /user/login

```
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST /follow/{user_id}

```
Response (200):
{
  "id": "follow-uuid",
  "follower_id": "your-id",
  "following_id": "target-id",
  "status": "active",
  "created_at": "2024-01-15T10:35:00Z"
}
```

### GET /follow/followers/{user_id}

```
Response (200):
{
  "total": 150,
  "limit": 20,
  "data": [
    {
      "follower_id": "uuid",
      "follower_username": "jane_doe",
      "created_at": "2024-01-15T09:00:00Z"
    }
  ],
  "next_cursor": "uuid",
  "has_more": true
}
```

---

# Protection Layers

- Input Validation — Pydantic type checking
- JWT Verification — RS256 signature validation
- Token Expiration — Timestamp checking
- Blacklist Checking — Redis lookup
- Authorization — Resource ownership verification
- SQL Injection — SQLAlchemy ORM protection
- Data Integrity — Database constraints

---

# Implemented Mechanisms

- ✓ Password: Bcrypt (12 rounds) + salt
- ✓ Tokens: RS256 asymmetric encryption
- ✓ Brute-force: Account locking (5 attempts)
- ✓ Session: Token blacklisting on logout
- ✓ CSRF: Token-based validation
- ✓ SQL Injection: ORM parameterized queries
- ✓ Data Integrity: CHECK constraints

---

# 📦 Technology Stack

| Component | Technology | Version |
| :--- | :--- | :---: |
| **Framework** | `FastAPI` | `0.100+` |
| **Language** | `Python` | `3.9+` |
| **Database** | `PostgreSQL` | `14+` |
| **ORM** | `SQLAlchemy` | `2.0+` |
| **Caching** | `Redis` | `7+` |
| **Auth** | `PyJWT` | `2.8+` |
| **Password** | `Bcrypt` | `4.0+` |
| **Validation** | `Pydantic` | `2.0+` |
| **Async DB** | `asyncpg` | `0.28+` |

---

# Setup

### Clone repository
git clone https://github.com/shreyajagtap758-sys/instagram-backend.git
cd instagram-backend

### Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### Install dependencies
pip install -r requirements.txt

### Create .env file
cp .env.example .env

### Generate JWT keys
openssl genrsa -out server/src/core/keys/private_key.pem 2048
openssl rsa -in server/src/core/keys/private_key.pem -pubout -out server/src/core/keys/public_key.pem

### Run migrations
- alembic upgrade head

### Start server
- uvicorn server.main:app --reload

### Docker Setup
- docker-compose up -d

---

# 📊 Performance

### Database Optimization

- Indexed queries for fast lookups
- Cursor-based pagination (O(log n))
- Denormalized counts (no aggregation)
- Connection pooling
- Prepared statements via ORM

### Caching

- Redis blacklist (instant revocation)
- Active session tracking
- Token management
- TTL-based auto-cleanup

### Scalability

- Stateless API design
- Horizontal scaling ready
- External Redis support
- Database read replicas compatible

---

# 📝 API Documentation

## Interactive docs available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

- Fork the repository
- Create feature branch (git checkout -b feature/amazing-feature)
- Commit changes (git commit -m 'Add amazing feature')
- Push to branch (git push origin feature/amazing-feature)
- Open Pull Request

---

# 👨‍💻 Author
## Shreya Jagtap

Email: shreyajagtap758@gmail.com
GitHub: @shreyajagtap758-sys

---

<div align="center">
Made with ❤️ for scalable backend systems

⭐ Star this repository if you find it helpful!

</div> ```
