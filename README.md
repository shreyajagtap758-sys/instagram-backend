Instagram Backend API
Overview

This project is a backend system for an Instagram-like application built using Python. It is designed with production-style backend architecture in mind, focusing on authentication security, token safety, modular design, and future scalability.

The system currently implements a complete authentication flow (signup, login, token generation, refresh, logout) with strong security practices like RSA-based JWT signing, token hashing, and Redis-based blacklist management.



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

The current system acts as the core authentication backbone for the future full-scale application.