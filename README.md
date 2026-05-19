<div align="center">

<img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/instagram.svg" width="80" height="80" alt="Instagram Backend" style="filter: drop-shadow(0 0 20px rgba(225, 48, 108, 0.4));">

# 📸 Instagram Backend

### Production-Ready Social Media API Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white&style=for-the-badge)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?logo=postgresql&logoColor=white&style=for-the-badge)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7%2B-DC382D?logo=redis&logoColor=white&style=for-the-badge)](https://redis.io)
[![MinIO](https://img.shields.io/badge/MinIO-S3%20Compatible-C72E49?logo=minio&logoColor=white&style=for-the-badge)](https://min.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**A scalable, secure, and enterprise-grade backend system for Instagram-like social media platforms.**

[Features](#-features) • [Architecture](#-architecture) • [API Reference](#-api-reference) • [Security](#-security) • [Setup](#-setup) • [Performance](#-performance)

</div>

---

## 🎯 Overview

A **production-ready backend system** engineered for Instagram-like social media platforms. Built with production-oriented architecture focused on authentication, transactional consistency, scalable media handling, authorization correctness, and operational reliability.

### Why This Project?

| Feature | Description |
|---------|-------------|
| ⚡ **Async-First** | FastAPI for high-throughput concurrent request handling |
| 🔐 **Enterprise Security** | JWT (RS256), MFA (TOTP), brute-force protection, session hardening |
| 💾 **Smart Caching** | Redis token blacklisting, rate limiting, and session management |
| 📊 **Scalable Database** | PostgreSQL with optimized indexes, cursor-based snapshot pagination, denormalized counters, and N+1-safe query loading |
| 🛡️ **Resilient Architecture** | Service-layer transaction orchestration, concurrency-safe mutations, retry-safe cleanup workflows, and structured exception handling |
| 📦 **Direct-to-Storage Media** | Private-bucket media architecture using signed upload/access URLs — backend never handles raw media bytes |
| 🔄 **S3-Compatible Design** | Storage layer abstracted for seamless migration to AWS S3 or Cloudflare R2 |
| 👥 Centralized Visibility Enforcement | Follower-aware authorization with account-level privacy, per-post visibility, and reusable access-control validation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web App    │  │ Mobile App   │  │   CLI Tool   │  │  Third-Party │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │                 │
          └─────────────────┴────────┬────────┴─────────────────┘
                                     │ HTTPS / REST API
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (FastAPI)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │   Posts      │  │   Follow     │  │   Password   │     │
│  │   Router     │  │   Router     │  │   Router     │  │   Router     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │                 │
          └─────────────────┴────────┬────────┴─────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   SERVICE LAYER  │      │   SERVICE LAYER  │      │   SERVICE LAYER  │
│  (Atomic Txns)   │      │  (Atomic Txns)   │      │  (Atomic Txns)   │
│                  │      │                  │      │                  │
│ • UserService    │      │ • PostService    │      │ • FollowService  │
│ • TokenService   │      │ • MediaService   │      │ • PasswordService│
│ • AuthService    │      │ • UploadService  │      │                  │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   REPOSITORY    │      │   REPOSITORY    │      │   REPOSITORY    │
│   (Data Access)  │      │   (Data Access)  │      │   (Data Access)  │
│                  │      │                  │      │                  │
│ • UserRepo       │      │ • PostRepo       │      │ • FollowRepo     │
│ • TokenRepo      │      │ • MediaRepo      │      │ • PasswordRepo   │
│ • RedisRepo      │      │ • UploadRepo     │      │                  │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   PostgreSQL    │      │     Redis       │      │     MinIO       │
│   (Primary DB)   │      │   (Cache/Queue)  │      │ (Object Store)  │
│                  │      │                  │      │                 │
│ • Users          │      │ • Token Blacklist│      │ • Media Objects │
│ • Posts          │      │ • Rate Limiters  │      │ • Signed URLs   │
│ • Follows        │      │ • Session State  │      │ • Private Bucket│
│ • Sessions       │      │                  │      │                 │
│ • Media Uploads  │      │                  │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

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
│           ├── redis.py                   # Redis utilities
│           ├── tokens.py                  # Token utilities
│           └── validations.py             # Input validation
```

---

## ✨ Features

<details>
<summary><h3 style="display:inline">👤 1. User Authentication & Management</h3></summary>

#### Core Capabilities
- ✅ **Password Change Flow** — Authenticated password updates with current-password verification
- ✅ **User Registration** — Email/username validation with uniqueness checks
- ✅ **Secure Login** — JWT-based authentication using RS256 asymmetric signing
- ✅ **Password Hashing** — Argon2-based password hashing with memory-hard protection
- ✅ **Brute-Force Protection** — Account locking after 5 failed attempts (15-min lockout)
- ✅ **Session Management** — DB-backed session lifecycle control with `sid`-based identification
- ✅ **Concurrent Session Limit** — Max 5 active sessions per user with oldest-session eviction
- ✅ **Logout & Revocation** — DB-backed session invalidation with Redis-based access token blacklisting
- ✅ **Refresh Token Rotation** — Single-use refresh tokens with atomic handling
- ✅ **Reuse Detection** — Refresh token reuse detection with automatic session invalidation
- ✅ **Rate Limiting** — Refresh endpoint protection against abuse and DB overload
- ✅ **Atomic Refresh Handling** — Concurrency-safe refresh rotation prevents duplicate token races
- ✅ **Global Session Revocation** — Security events trigger invalidation of all active user sessions
- ✅ **Password Reset Security** — Single-use reset tokens with atomic validation and replay protection
- ✅ **Session Invalidation on Password Reset** — Existing sessions revoked after successful password reset
- ✅ **Session-Bound Refresh Tokens** — Refresh token lifecycle tied to persistent session records

#### Database Schema

**`users` Table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, INDEXED | User email address |
| `username` | VARCHAR(50) | UNIQUE, INDEXED | Public display name |
| `hashed_password` | VARCHAR(255) | NOT NULL | Argon2-hashed password |
| `is_locked` | BOOLEAN | DEFAULT FALSE | Brute-force lock status |
| `lock_until` | TIMESTAMP | NULLABLE | Auto-unlock timestamp |
| `failed_login_attempts` | INTEGER | DEFAULT 0 | Failed attempt counter |
| `last_login` | TIMESTAMP | NULLABLE | Last successful login |
| `follower_count` | INTEGER | DEFAULT 0 | Denormalized follower count |
| `following_count` | INTEGER | DEFAULT 0 | Denormalized following count |
| `status` | VARCHAR(20) | DEFAULT 'active' | Account status |
| `is_private` | BOOLEAN | DEFAULT FALSE | Account-level privacy control |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Registration timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

</details>

---

<details>
<summary><h3 style="display:inline">🔐 2. Security & Authentication</h3></summary>

#### JWT Token Architecture (RS256)

```
┌─────────────────────────────────────────────────────────────┐
│                    TOKEN LIFECYCLE                           │
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │   ISSUE     │───▶│   VALIDATE  │───▶│   ROTATE    │    │
│   │             │    │             │    │             │    │
│   │ • RS256     │    │ • Signature │    │ • Single-use│    │
│   │ • 15m TTL   │    │ • Expiry    │    │ • Atomic    │    │
│   │ • 7d Refresh│    │ • Blacklist │    │ • Reuse     │    │
│   │ • jti claim │    │ • Session   │    │   detect    │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Component | Specification |
|-----------|---------------|
| **Algorithm** | RSA Signature with SHA-256 (RS256) |
| **Access Token TTL** | 15 minutes |
| **Refresh Token TTL** | 7 days |
| **Token Claims** | `sub` (user ID), `exp` (expiry), `jti` (unique token ID) |
| **Key Management** | Asymmetric key pair (2048-bit RSA) |
| **Rotation** | Atomic single-use refresh with reuse detection |
| **Blacklisting** | Redis-backed instant revocation with TTL auto-cleanup |

#### Password Security

| Parameter | Value |
|-----------|-------|
| **Algorithm** | Argon2id |
| **Memory Cost** | 64 MB |
| **Time Cost** | 3 iterations |
| **Parallelism** | 4 threads |

**Password Requirements:**
- ✓ Minimum 8 characters
- ✓ At least 1 uppercase letter (A-Z)
- ✓ At least 1 digit (0-9)
- ✓ At least 1 special character (`!@#$%^&*`)

#### Security Mechanisms

| Layer | Implementation | Protection |
|-------|---------------|------------|
| **Brute-Force** | Account locking (5 attempts → 15 min lock) | Credential stuffing |
| **Token Blacklist** | Redis string-key blacklist with TTL matching token expiry | Instant revocation |
| **Session Control** | DB-backed `sid` tracking, max 5 concurrent | Session hijacking |
| **Rate Limiting** | Redis atomic INCR/EXPIRE fixed-window rate limiting | Token spamming & upload abuse |
| **Password Reset** | Atomic one-time tokens (15-min expiry) | Replay attacks |
| **SQL Injection** | SQLAlchemy ORM parameterized queries | Injection attacks |
| **Data Integrity** | Database CHECK constraints | Corrupt data |
| **Media Validation** | Object ownership, existence, extension, and uploaded size validation | Unauthorized media attachment |
| **Visibility Enforcement** | Centralized follower-aware authorization checks | Private content leakage |
| **Replay Detection** | Refresh token reuse detection with global session invalidation | Stolen refresh token replay |

</details>

---

<details>
<summary><h3 style="display:inline">👥 3. Follow System</h3></summary>

#### Core Capabilities
- ✅ **Follow/Unfollow** — Persistent follower graph management with relationship lifecycle tracking
- - ✅ **Private Account Authorization** — Follow relationships integrated with centralized post visibility enforcement
- ✅ **Self-Follow Prevention** — Database-level `CHECK` constraint
- ✅ **Duplicate Prevention** — Unique composite index on `(follower_id, following_id)`
- ✅ **Paginated Lists** — Cursor-based pagination for followers/following
- ✅ **Optimized Relationship Queries** — Indexed follower/following lookups for scalable pagination
- ✅ **Soft Delete** — Status-based deletion with `deleted_at` timestamp
- ✅ **Relationship Lifecycle Tracking** — Status-based follow lifecycle with soft-delete timestamps
- ✅ **Private Account Foundations** — Relationship model supports pending/accepted follow states for private account authorization
- ✅ **Follower-Aware Authorization** — Follow graph integrated with account-level and per-post visibility enforcement

#### Database Schema

**`follows` Table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique follow ID |
| `follower_id` | UUID | FOREIGN KEY → users.id | The follower |
| `following_id` | UUID | FOREIGN KEY → users.id | The followed user |
| `status` | VARCHAR(20) | DEFAULT 'active' | Relationship status |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Follow timestamp |
| `deleted_at` | TIMESTAMP | NULLABLE | Soft-delete timestamp |

**Constraints:**
```sql
UNIQUE (follower_id, following_id)    -- Prevent duplicate follows
CHECK (follower_id != following_id)   -- Prevent self-follow
ON DELETE CASCADE                     -- Clean up on user deletion
```

</details>

---

<details>
<summary><h3 style="display:inline">📸 4. Post & Media System</h3></summary>

#### Core Capabilities
- ✅ **CRUD Operations** — Create, read, update (caption/visibility), soft-delete posts
- ✅ **Direct-to-Storage Upload** — Frontend uploads directly to MinIO via signed URLs
- ✅ **Signed Access URLs** — Temporary authenticated media rendering for private buckets
- ✅ **Object Validation** — Ownership, existence, extension, and size validation before persistence
- ✅ **Media Lifecycle Tracking** — `pending → attached` state transitions with orphan cleanup
- ✅ **Visibility Architecture** — Account-level privacy + per-post visibility with follower-aware enforcement
- ✅ **Snapshot-Consistent Pagination** — Stable cursor pagination using `created_at DESC, id DESC` ordering
- ✅ **Concurrency-Safe Mutations** — Atomic conditional update queries prevent stale update/delete race conditions
- ✅ **Rate Limiting** — Redis fixed-window limiter on upload URL generation
- ✅ **N+1 Safe Loading** — Optimized `selectinload` relationship loading
- ✅ **Retention-Based Deletion** — Soft delete → delayed hard delete with asynchronous storage cleanup
- ✅ **Retry-Safe Cleanup Workflows** — Partial cleanup failures do not rollback successful storage deletions

#### Media Upload Flow

```
┌──────────┐     1. Request URL      ┌──────────┐
│  Client  │ ──────────────────────▶ │  Backend │
│          │                         │          │
│          │ ◀──── 2. Signed URL ─── │          │
│          │    + Object Key         │          │
└────┬─────┘                         └──────────┘
     │
     │ 3. Direct Upload
     ▼
┌──────────┐
│  MinIO   │
│ (Private)│
└────┬─────┘
     │
     │ 4. Confirm Upload
     ▼
┌──────────┐     5. Create Post      ┌──────────┐
│  Client  │ ──────────────────────▶ │  Backend │
│          │    (with object key)    │          │
│          │                         │  Validate│
│          │                         │  • Owner │
│          │                         │  • Exists│
│          │                         │  • Ext   │
│          │                         │  • Size  │
│          │ ◀──── 6. Post Created ─ │          │
└──────────┘                         └──────────┘
```

#### Media Lifecycle

```
PENDING UPLOAD
      │
      ▼ (Frontend uploads to MinIO)
ATTACHED TO POST
      │
      ▼ (Post created successfully)
ACTIVE POST
      │
      ▼ (User deletes post)
SOFT DELETE (status='deleted')
      │
      ▼ (Retention window expires)
HARD DELETE + STORAGE CLEANUP
```
**Orphan uploads** (uploaded but never attached to posts) are cleaned independently through scheduled lifecycle cleanup.


#### Visibility Architecture

| Level | Setting | Authorization Check |
|-------|---------|---------------------|
| **Account** | `public` / `private` | Global profile visibility |
| **Post** | `public` / `private` | Per-post visibility control |
| **Follower-Aware** | Private account | `is_following()` check required |
| **Centralized** | Single function | `validate_post_visibility()` + `can_view_post()` |

#### Database Schema

**`posts` Table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique post ID |
| `author_id` | UUID | FOREIGN KEY → users.id | Post creator |
| `caption` | TEXT | NULLABLE | Post caption |
| `visibility` | VARCHAR(20) | DEFAULT 'public' | Post visibility |
| `status` | VARCHAR(20) | DEFAULT 'published' | Post status |
| `like_count` | INTEGER | DEFAULT 0 | Denormalized like count |
| `comment_count` | INTEGER | DEFAULT 0 | Denormalized comment count |
| `deleted_at` | TIMESTAMP | NULLABLE | Soft-delete timestamp |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**`post_media` Table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique media ID |
| `post_id` | UUID | FOREIGN KEY → posts.id | Parent post |
| `object_key` | VARCHAR(500) | NOT NULL | MinIO object key |
| `media_type` | VARCHAR(20) | NOT NULL | `image` or `video` |
| `order_index` | INTEGER | DEFAULT 0 | Display order |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Upload timestamp |

**`media_uploads` Table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique upload ID |
| `author_id` | UUID | FOREIGN KEY → users.id | Uploader |
| `object_key` | VARCHAR(500) | UNIQUE | MinIO object key |
| `media_type` | VARCHAR(20) | NOT NULL | Declared media type |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Upload lifecycle state |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Upload timestamp |

</details>

---

<details>
<summary><h3 style="display:inline">🔑 5. Password Management</h3></summary>

#### Core Capabilities
- ✅ **Change Password** — Requires current password verification
- ✅ **Forgot Password** — Email-based secure reset flow
- ✅ **Atomic Token Consumption** — One-time reset token usage with race-condition safety
- ✅ **Token Expiry** — 15-minute short-lived tokens
- ✅ **Single Active Reset Token** — Previous reset tokens invalidated when a new token is issued
- ✅ **Global Session Revocation** — All active sessions invalidated after successful password reset
- ✅ **Replay Protection** — Previously consumed reset tokens cannot be reused
- ✅ **Reset Token Rotation** — New password reset requests automatically invalidate older reset links

#### Password Reset Flow

```
┌──────────┐                          ┌──────────┐
│   User   │  1. Request Reset        │  Backend │
│          │ ───────────────────────▶ │          │
│          │                          │ Generate │
│          │ ◀── 2. Email with Link ─ │  Token   │
│          │                          │ (15 min) │
└────┬─────┘                          └──────────┘
     │
     │ 3. Click Link
     ▼
┌──────────┐  4. Submit New Password  ┌──────────┐
│   User   │ ───────────────────────▶ │  Backend │
│          │                          │ Validate │
│          │                          │ • Token  │
│          │                          │ • Strength│
│          │ ◀── 5. Password Updated ─│ Atomic   │
│          │                          │ token +  │
│          │                          │ password │
│          │                          │ update   │
└──────────┘                          └────┬─────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ Invalidate   │
                                    │ • All Sessions│
                                    │ • All Reset  │
                                    │   Tokens     │
                                    └──────────────┘
```

</details>

---

## 🔌 API Reference

### Authentication (`/user`)

| Method | Endpoint | Description | Auth |
|:------:|:---------|:------------|:----:|
| `POST` | `/user/signup` | Create a new account | ❌ |
| `POST` | `/user/login` | Authenticate & receive tokens | ❌ |
| `GET` | `/user/me` | Retrieve current user profile | ✅ |
| `POST` | `/user/get_new_access_token` | Refresh expired access token | ❌ |
| `POST` | `/user/logout` | End session & revoke tokens | ✅ |

### Password Management (`/password`)

| Method | Endpoint | Description | Auth |
|:------:|:---------|:------------|:----:|
| `POST` | `/password/change-password` | Change password | ✅ |
| `POST` | `/password/forgot-password` | Request password reset | ❌ |
| `POST` | `/password/reset-password` | Reset with one-time token | ❌ |

### Social & Follow (`/follow`)

| Method | Endpoint | Description | Auth |
|:------:|:---------|:------------|:----:|
| `POST` | `/follow/{user_id}` | Follow a user | ✅ |
| `DELETE` | `/follow/{user_id}` | Unfollow a user | ✅ |
| `GET` | `/follow/followers/{user_id}` | Get followers list | <sub>Optional*</sub> |
| `GET` | `/follow/following/{user_id}` | Get following list | <sub>Optional*</sub> |

### Posts & Media (`/post`)

| Method | Endpoint | Description | Auth |
|:------:|:---------|:------------|:----:|
| `POST` | `/post/generate_upload_url` | Generate signed direct-upload URL for media upload | ✅ |
| `POST` | `/post/create_post` | Create post using uploaded object keys | ✅ |
| `GET` | `/post/get_post/{post_id}` | Retrieve single post with signed media access URLs | <sub>Optional*</sub> |
| `GET` | `/post/get_user_post/{user_id}` | Get paginated user posts with visibility filtering | <sub>Optional*</sub> |
| `PATCH` | `/post/update_post/{post_id}` | Update caption & visibility | ✅ |
| `DELETE` | `/post/delete_post/{post_id}` | Soft delete post | ✅ |

> **<sub>*Optional Auth:</sub>** Public content is accessible without authentication. Private account or post visibility requires authenticated follower-based authorization checks.

---

## 🛡️ Security

### Protection Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      DEFENSE IN DEPTH                            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1 │ Input Validation        │ Pydantic type checking      │
│  Layer 2 │ JWT Verification        │ RS256 signature validation  │
│  Layer 3 │ Token Expiration        │ Timestamp checking          │
│  Layer 4 │ Blacklist Checking      │ Redis lookup (revocation)   │
│  Layer 5 │ Authorization           │ Resource ownership validation│
│  Layer 6 │ SQL Injection           │ SQLAlchemy ORM protection   │
│  Layer 7 │ Data Integrity          │ Database constraints        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 8 │ Refresh Token Rotation  │ Single-use enforcement      │
│  Layer 9 │ Reuse Detection         │ Stolen token detection      │
│  Layer 10│ Rate Limiting           │ Refresh endpoint protection │
│  Layer 11│ Session Control         │ DB-backed bounded sessions  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 12│ Signed Upload URLs      │ Time-limited direct upload  │
│  Layer 13│ Signed Access URLs      │ Private-bucket media rendering│
│  Layer 14│ Object Ownership        │ Prevents cross-user attach  │
│  Layer 15│ Object Existence        │ Validates before persistence│
│  Layer 16│ Upload Size Validation  │ Real object-size enforcement│
│  Layer 17│ Extension Validation    │ Type consistency check      │
│  Layer 18│ Upload Rate Limiting    │ Redis INCR/EXPIRE limiter   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 19│ Visibility Enforcement  │ Follower-aware auth checks  │
│  Layer 20│ Concurrency Protection  │ Atomic conditional updates  │
│  Layer 21│ Soft Delete Lifecycle   │ Delayed hard deletion       │
│  Layer 22│ Retry-Safe Cleanup      │Orphan+delayed cleanup recovery│
└─────────────────────────────────────────────────────────────────┘
```

### Implemented Mechanisms

| Category | Mechanism | Status |
|----------|-----------|:------:|
| **Password** | Argon2id memory-hard password hashing | ✅ |
| **Tokens** | RS256 asymmetric token signing | ✅ |
| **Brute-Force** | Account locking (5 attempts) | ✅ |
| **Session** | DB-backed `sid` management with logout invalidation | ✅ |
| **SQL Injection** | ORM parameterized queries | ✅ |
| **Data Integrity** | CHECK constraints | ✅ |
| **Refresh** | Atomic rotation with reuse detection | ✅ |
| **Session Limits** | Bounded concurrent session enforcement (max 5) | ✅ |
| **Rate Limiting** | Redis fixed-window protection for refresh and upload endpoints | ✅ |
| **Reset Tokens** | Single-use with atomic validation | ✅ |
| **Media Uploads** | Signed direct-to-storage architecture | ✅ |
| **Media Access** | Temporary signed URLs for private-bucket media rendering | ✅ |
| **Upload Abuse** | Redis fixed-window rate limiting | ✅ |
| **Object Validation** | Ownership, existence, extension, and uploaded size validation | ✅ |
| **Media Lifecycle** | Pending → attached state tracking | ✅ |
| **Pagination** | Snapshot-consistent cursor pagination | ✅ |
| **Visibility** | Centralized follower-aware enforcement | ✅ |
| **Concurrency** | Atomic conditional update queries | ✅ |
| **Cleanup** | Retry-safe orphan + delayed storage cleanup | ✅ |
| **Deletion** | Soft delete → retention → hard delete | ✅ |
| **Upload Tracking** | Persistent pending → attached upload lifecycle modeling | ✅ |
| **Transactions** | Service-layer atomic transaction orchestration | ✅ |

---

## 📦 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|:-------:|:--------|
| **Framework** | FastAPI | `0.100+` | Async web framework |
| **Language** | Python | `3.9+` | Runtime |
| **Database** | PostgreSQL | `14+` | Primary data store |
| **ORM** | SQLAlchemy | `2.0+` | Async ORM and query construction |
| **Redis Infrastructure** | Redis | `7+` | Access-token blacklist and fixed-window rate limiting |
| **Object Storage** | MinIO | `latest` | S3-compatible media storage |
| **JWT Handling** | PyJWT | `2.8+` | RS256 token signing and validation |
| **Password Hashing** | Argon2 | `latest` | Secure password hashing |
| **Validation** | Pydantic | `2.0+` | Typed request validation and response schemas |
| **Async DB** | asyncpg | `0.28+` | Async PostgreSQL driver |
| **Migrations** | Alembic | `latest` | Database schema versioning |

---

## 🚀 Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Redis 7+
- MinIO (or any S3-compatible object storage)
- Docker (optional, for local MinIO setup)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/shreyajagtap758-sys/instagram-backend.git
cd instagram-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database, Redis, and MinIO credentials

# 5. Start MinIO (Docker)
docker run -p 9000:9000 -p 9001:9001 \\
  -e "MINIO_ROOT_USER=minioadmin" \\
  -e "MINIO_ROOT_PASSWORD=minioadmin" \\
  quay.io/minio/minio server /data --console-address ":9001"

# 6. Create bucket
# Visit http://localhost:9001 and create bucket: instagram-media

# Keep bucket private — media access is handled through signed access URLs

# 7. Generate JWT keys
openssl genrsa -out server/src/core/keys/private_key.pem 2048
openssl rsa -in server/src/core/keys/private_key.pem -pubout \\
  -out server/src/core/keys/public_key.pem

# Ensure PostgreSQL and Redis are running before starting the application

# 8. Run migrations
alembic upgrade head

# 9. Start server
uvicorn server.main:app --reload
```

### Docker Compose (One-Command Setup)

```bash
docker-compose up -d
```

### API Documentation

Once running, explore the interactive API documentation:

| Documentation | URL |
|--------------|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **MinIO Console** | http://localhost:9001 |

---

## 📊 Performance

### Database Optimizations

| Technique | Implementation | Impact |
|-----------|---------------|--------|
| **Indexed Queries** | B-tree indexes on `email`, `username`, `follower_id`, `following_id` | O(log n) lookups |
| **Cursor Pagination** | Snapshot-consistent `created_at DESC, id DESC` ordering | Stable pagination during concurrent writes |
| **Denormalized Counts** | `follower_count`, `following_count` on users table | No aggregation queries |
| **Connection Pooling** | Asyncpg pool management | Reduced connection overhead |
| **Parameterized Queries** | SQLAlchemy ORM query generation | Safe and optimized query execution |
| **Relationship Loading** | `selectinload` for media | N+1 query prevention |
| **Atomic Updates** | Conditional `UPDATE ... WHERE` queries | Prevents stale concurrent mutations |

### Caching Strategy

| Cache Type | Storage | TTL | Purpose |
|-----------|---------|-----|---------|
| **Token Blacklist** | Redis String | Token expiry | Instant revocation |
| **Rate Limit** | Redis String | Window size | Abuse protection |
| **Upload Limit** | Redis String | Window size | Upload spam prevention |

### Scalability Features

| Feature | Benefit |
|---------|---------|
| **Stateless API** | Horizontal scaling without session affinity |
| **External Redis** | Shared blacklist and rate-limiting infrastructure across API instances |
| **Read Replicas** | PostgreSQL read replica compatibility |
| **Direct-to-Storage** | Backend never handles media bytes — scales independently |
| **S3-Compatible** | Seamless migration to AWS S3 / Cloudflare R2 |
| **Async Cleanup** | Media lifecycle decoupled from request handling |
| **Retry-Safe Cleanup** | Partial cleanup failures do not rollback successful operations |
| **Upload Limit** | Redis String (`INCR/EXPIRE`) | Fixed window | Upload abuse protection |

---

## 📈 System Characteristics

```
┌─────────────────────────────────────────────────────────────┐
│                   ARCHITECTURAL PROPERTIES                  │
├─────────────────────────────────────────────────────────────┤
│ Authentication                                              │
│ ├── RS256 JWT signing and validation                        │
│ ├── Redis-backed blacklist revocation                       │
│ └── Atomic refresh token rotation                           │
│                                                             │
│ Media Architecture                                          │
│ ├── Direct-to-storage uploads (backend bypass)              │
│ ├── Signed upload and access URL generation                 │
│ └── Private-bucket media delivery                           │
│                                                             │
│ Pagination & Queries                                        │
│ ├── Snapshot-consistent cursor pagination                   │
│ ├── Indexed relationship lookups                            │
│ └── N+1-safe relationship loading                           │
│                                                             │
│ Data Consistency                                            │
│ ├── Atomic conditional update queries                       │
│ ├── Service-layer transaction orchestration                 │
│ └── Retry-safe cleanup workflows                            │
│                                                             │
│ Scalability                                                 │
│ ├── Stateless API architecture                              │
│ ├── Redis-backed distributed rate limiting                  │
│ └── S3-compatible storage abstraction                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Ensure all security mechanisms remain intact
- Preserve transaction safety and authorization consistency in all changes

---

## 👨‍💻 Author

**Shreya Jagtap**

- 📧 Email: [shreyajagtap758@gmail.com](mailto:shreyajagtap758@gmail.com)
- 🐙 GitHub: [@shreyajagtap758-sys](https://github.com/shreyajagtap758-sys)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Made with ❤️ for scalable backend systems

If you find this project helpful, please consider giving it a ⭐!

[![GitHub stars](https://img.shields.io/github/stars/shreyajagtap758-sys/instagram-backend?style=social)](https://github.com/shreyajagtap758-sys/instagram-backend/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/shreyajagtap758-sys/instagram-backend?style=social)](https://github.com/shreyajagtap758-sys/instagram-backend/network/members)

</div>
'''
