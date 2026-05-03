Instagram Backend API
Overview
# 🛡️ Secure Authentication Backend (FastAPI) Upgrade

This project is a backend system for an Instagram-like application built using Python. It is designed with production-style backend architecture in mind, focusing on authentication security, token safety, modular design, and future scalability.
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00C7B7?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

The system currently implements a complete authentication flow (signup, login, token generation, refresh, logout) with strong security practices like RSA-based JWT signing, token hashing, and Redis-based blacklist management.
A production-oriented authentication system built with FastAPI implementing **JWT rotation, Redis session control, and secure password lifecycle management**.

---

# 📌 Architecture Overview

## 🧱 System Flow

```text
Client
  ↓
FastAPI Routes
  ↓
Service Layer (Business Logic)
  ↓
Repository Layer (DB Operations)
  ↓
PostgreSQL + Redis
  ↓
Email Gateway (SMTP/FastMail)



🔐 Authentication Flow

Login
  ↓
Access Token + Refresh Token
  ↓
API Requests (Access Token)
  ↓
Refresh Token Rotation (if expired)
  ↓
Redis Blacklist Validation


🔁 Password Reset Flow

Forgot Password Request
  ↓
Secure Token Generation (SHA-256 hashed storage)
  ↓
Email Sent (Frontend Reset Link)
  ↓
Frontend Page (/reset-password/:token)
  ↓
Token Verification
  ↓
Password Update
  ↓
Token Invalidation (Single Use)


🚀 Features


🔐 Security Core

JWT-based authentication (RS256)
Refresh token rotation system
Token reuse detection
Redis-based blacklist (O(1) lookup)
Argon2 password hashing

🔁 Session Management

Stateless access tokens
Stateful refresh token tracking
Automatic token revocation on reuse
Device/session integrity enforcement

📧 Password Reset System

One-time secure tokens
SHA-256 hashed storage
Expiry-based validation
Email-based reset workflow

🛡️ Validation Engine

Strong password policy enforcement
Username format validation
Email normalization
Dictionary attack prevention


Updated Project Structure Where Changes Were Made


Project Structure
```
instagram/
│
├── server/
│   ├── main.py
│   ├── src/
│       ├── core/
│       │   ├── AuthSecurity/
│       │   │   ├── auth.py
│       │   │   └── security.py
│       │   ├── db/
│       │   │   └── database.py
│       │   ├── config.py
│       │   ├── redis.py
│       │   └── keys/
│       │       └── generate keys (private.pem, public.pem)
│       │
│       ├── models/
│       │   ├── base.py
│       │   ├── user.py
│       │   ├── refresh.py
│       │   └── __init__.py
│       │
│       ├── repository/
│       │   ├── user.py
│       │   ├── token.py
│       │   └── redis.py
│       │
│       ├── services/
│       │   ├── users.py
│       │   └── tokens.py
│       │
│       ├── routes/
│       │   └── user.py
│       │
│       ├── schemas/
│       │   └── user.py
│       │
│       ├── utils/
│       │   └── dependency.py
│       │
│       └── __init__.py
│
├── alembic/
│   ├── env.py
│   └── versions/
│       └── initial migration setup
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── .env (not tracked)
├── .gitignore
└── .venv
```


Authentication System (Core Logic)
Password Security
Passwords are hashed using Passlib with Argon2
Argon2 is used because it is resistant to GPU-based brute force attacks
Verification is done using secure hash comparison instead of plain text matching
Token System (JWT + RSA)
Access Token
Created using JWT (RS256 algorithm)
Signed using private RSA key
Includes:
user id (sub)
email
unique token id (jti)
expiration time (exp)

👉 RS256 is used instead of HS256 because:

Private key signs tokens
Public key verifies tokens
More secure for distributed systems
Refresh Token
Also JWT-based but stored securely in DB
Contains:
user id
jti (unique token identifier)
type = refresh
expiry time

👉 Purpose:

Used to generate new access tokens without re-login
Refresh Token Security
Refresh tokens are hashed using SHA256 before storing in database
Reason:
If DB leaks, raw tokens cannot be misused
Only hash is stored, never raw token
Token Rotation System

When refresh token is used:

Old refresh token is validated
It is checked in DB using its SHA256 hash
It is marked as revoked = True
New access + refresh tokens are generated
New refresh token is stored again (hashed)

👉 This prevents reuse of old tokens (prevents replay attacks)

Logout System
Uses JWT jti (unique token ID)
On logout:
token is added to Redis blacklist
stored with expiry time of token
Redis ensures:
fast lookup
automatic expiration cleanup

👉 This ensures logged-out tokens cannot be reused even if still valid

Account Security Layer
Failed Login Protection
Tracks failed login attempts in database
After threshold (5 attempts):
account is locked
lock duration = 15 minutes
Lock System
Prevents brute force password attacks
Automatically unlocks after timeout
Database Layer
Built using SQLAlchemy async ORM
Async session management used for scalability
Models include:
User
RefreshToken
User Model Security Fields
hashed_password → stores Argon2 hash
failed_login_attempts → tracks brute force attempts
is_locked + lock_until → account lock system
last_login → tracks login activity
Refresh Token Model
token_hash → SHA256 hashed refresh token
revoked → prevents reuse
expires_at → token lifetime control
Redis Usage

Redis is used for:

Token blacklist storage
Fast token invalidation

Why Redis:

In-memory speed
Auto expiry support
Perfect for authentication caching layer
Key Management (RSA)
Private and Public RSA keys are generated using Python cryptography module
Stored in .pem files
Private key:
used only for signing JWT tokens
Public key:
used for verifying tokens

👉 These keys are NOT committed to GitHub for security reasons

API Layer

The API includes:

/signup → user registration
/login → authentication + token generation
/me → current user info
/logout → token invalidation
/get_access_token → refresh token rotation
Design Philosophy

This backend is built with:

Separation of concerns (routes, services, repository layers)
Security-first authentication design
Stateless access tokens + stateful refresh tokens
Scalable async architecture
Real-world production patterns instead of tutorial-style code
Current Status

The authentication system is fully functional and secure.
Other modules (posts, messaging, media system, etc.) are planned but not yet implemented.



⚙️ Tech Stack

FastAPI (Backend Framework)
PostgreSQL (Primary Database)
Redis (Token blacklist + caching)
JWT (Authentication)
Argon2 (Password hashing)
Docker (Containerization)

📧 Email System

SMTP / FastMail integration
HTML email templates
Tokenized password reset links
Centralized email gateway module

🚦 Error Handling

Granular exception system
Field-level validation errors
Clear API responses for frontend
Structured failure responses (no generic errors)

🧠 Key Design Principles

Zero-trust authentication model
Strict token lifecycle enforcement
Layered architecture (Separation of Concerns)
Stateless where possible, stateful where necessary
Secure-by-default design

🐳 Deployment (Docker)


🔧 Build & Run

docker compose up --build

📦 Services Included

FastAPI backend
PostgreSQL database
Redis cache
Email service integration


🌐 Environment Variables


Create .env file:

DATABASE_URL=postgresql://user:password@db:5432/app
REDIS_URL=redis://redis:6379
SECRET_KEY=your_secret
ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
MAIL_FROM=your_email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

FRONTEND_URL=http://localhost:5173


📊 Security Highlights

No plaintext password storage
Hashed reset tokens only
Redis-backed token invalidation
Strict JWT type enforcement
Session replay attack detection

🚀 Roadmap

OAuth2 (Google / GitHub login)
Multi-device session tracking
Rate limiting (Brute-force protection)
Admin audit dashboard
Real-time security logs



🧠 Summary

A modular, secure authentication system built for scalability, with strict token lifecycle control, layered architecture, and production-grade security patterns.