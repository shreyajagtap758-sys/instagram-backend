# 🛡️ Secure Authentication Backend (FastAPI) Upgrade

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00C7B7?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

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


├── server/
│   ├── src/
│   │   ├── core/
│   │   │   └── email_config.py      # Centralized SMTP gateway for FastMail 📧
│   │   ├── routes/
│   │   │   └── password_routes.py   # Dedicated Controllers for recovery & rotation
│   │   ├── services/
│   │   │   └── password_service.py  # Business Logic: Expiry, Token Validation, Mail Dispatch
│   │   ├── repository/
│   │   │   └── password_repo.py     # Data Access: Atomic CRUD (Pure DB Interactions) 🗄️
│   │   ├── models/
│   │   │   └── password_reset.py    # Relational Opaque Token schema with Foreign Keys
│   │   ├── schemas/
│   │   │   └── password_schema.py   # Pydantic blueprints for credential payloads
│   │   ├── utils/
│   │   │   └── validations.py       # Defensive Regex & Security Policy Engine 🛡️
│   │   └── error_handling/
│   │       └── exceptions/          # Granular ValidationException Framework
     

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