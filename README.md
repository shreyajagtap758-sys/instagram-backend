# Follow System (Instagram Clone Backend Module)

## Overview

This module implements a scalable follow/unfollow system similar to Instagram, designed with production-level considerations such as idempotency, race condition safety, cursor-based pagination, and snapshot isolation for consistent reads.

---

# Architecture Summary

The follow system is divided into 5 layers:

* Models (Database Layer)
* Repository (Query Layer)
* Service (Business Logic Layer)
* Schema (Request/Response Validation Layer)
* Routes (API Layer)

---

# 1. Models Layer

### File: `models/follow.py`

### What was added:

* Follow relationship table

### Fields:

* id
* follower_id (UUID)
* following_id (UUID)
* created_at
* updated_at
* deleted_at
* status
* is_muted

### Safety Constraints:

* UNIQUE(follower_id, following_id)
  → Prevents duplicate follows

* CHECK(follower_id != following_id)
  → Prevents self-follow

### Purpose:

Ensures data integrity at database level so invalid relationships never persist.

---

# 2. Repository Layer

### File: `repository/follow.py`

### What exists here:

* insert follow
* delete follow
* get followers
* get following

### Core Logic:

#### Cursor-based Pagination:

* Uses `created_at + follower_id` as cursor
* Ensures stable ordering

#### Snapshot Isolation:

* snapshot_time = max(created_at)
* Locks dataset at a point in time
* Prevents newly created follows from affecting old pagination

#### Query Safety:

* ORDER BY created_at ASC, follower_id ASC
* LIMIT applied per page

### Why this exists:

* Prevents missing or duplicate data during pagination
* Ensures consistent feed experience

---

# 3. Service Layer

### File: `service/follow.py`

### Responsibilities:

* Business logic handling
* Data transformation
* Error handling

### Key Logic:

#### Follow User:

* Prevent self-follow
* Check if user exists
* Insert follow relation
* Increment counters (if implemented)
* Handle IntegrityError → returns "already_following" instead of crash

#### Unfollow User:

* Safe delete (idempotent)
* No failure if relation does not exist

#### Get Followers / Following:

* Calls repository
* Extracts only required fields (follower_id / following_id)
* Builds next_cursor from last record

### Safety Mechanisms:

* Race condition safe via DB constraints
* Idempotent follow/unfollow behavior

---

# 4. Schema Layer

### File: `schema/follow.py`

### What was added:

#### PaginationSchema (Request)

* last_created_at
* last_id
* snapshot_time
* limit

Used for:

* controlling pagination input

---

#### FollowResponse

* status message only

---

#### FollowListResponse

* data: list of UUIDs
* next_cursor: pagination state

### Role of Schema:

* Validates API input/output
* Ensures type safety
* Prevents invalid requests reaching service layer

---

# 5. Routes Layer

### File: `routes/follow.py`

### Endpoints:

#### 1. Follow User

```
POST /follow/{user_id}
```

* Current user follows target user

#### 2. Unfollow User

```
DELETE /follow/{user_id}
```

* Removes follow relationship safely

#### 3. Get Followers

```
GET /follow/followers/{user_id}
```

* Returns list of followers with pagination

#### 4. Get Following

```
GET /follow/following/{user_id}
```

* Returns list of users being followed

### Flow:

Request → Schema validation → Service layer → Repository → DB → Response build

---

# 6. Key System Design Decisions

### 1. Cursor-based Pagination

* Avoids OFFSET inefficiency
* Scales to millions of rows

### 2. Snapshot Isolation

* Prevents shifting results during pagination
* Ensures consistent user experience

### 3. Idempotent Operations

* Follow repeated multiple times = safe
* Unfollow repeated = safe

### 4. Database-level Safety

* Unique constraints prevent duplicates
* Check constraints prevent invalid relations

---

# 7. Error Handling Strategy

### Implemented:

* IntegrityError → converted to safe response
* NoRelationFound exception for invalid unfollow
* Validation errors handled by schema layer

### Benefit:

* No raw DB errors exposed to API
* Stable production behavior

---

# 8. Summary

This follow system is designed as a production-ready social graph module with:

* Strong data integrity
* Scalable pagination
* Safe concurrent operations
* Clean layered architecture
* Predictable API behavior

---

# Status

✔ Production-oriented foundation implemented
⚠ Minor optimizations will be implemented (bulk queries, caching, feed integration)
