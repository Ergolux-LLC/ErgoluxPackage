# auth

# Project Architecture Overview

This project is structured using a layered architecture with a focus on clean separation of concerns. It uses SQLAlchemy Core for database interaction, CockroachDB as the primary data store, and Python `@dataclass` models to define the domain layer. This README explains the structure, responsibilities, and flow of control across the system.

---

## Directory Structure and Responsibilities

### `app/interfaces/relationaldb/relationaldb_repo.py`

- **Purpose**: Defines an abstract base class (`RelationalRepository`) that acts as the contract for all relational database interactions.
- **Role**: Serves as the interface that any concrete repository implementation must adhere to.
- **Benefit**: Enables easy swapping of database backends (e.g., CockroachDB, Postgres, mock databases) without changing the business logic.

---

### `app/interfaces/relationaldb/cockroachdb.py`

- **Purpose**: Implements the methods defined in `relationaldb_repo.py` using SQLAlchemy Core.
- **Role**: Provides the concrete logic for interacting with CockroachDB. Executes raw or expression-based SQL, then maps results into domain dataclasses.
- **Notes**:
  - Adheres strictly to the `RelationalRepository` interface.
  - Uses SQLAlchemy Core, not the ORM.
  - Uses `User.from_row()` for clean mapping from database rows to domain models.

---

### `app/domain/user.py`

- **Purpose**: Contains the `User` domain model as a Python `@dataclass`.
- **Role**: Represents user data used throughout the business logic layer.
- **Notes**:
  - Contains no persistence or database logic.
  - Implements a static method `from_row(row)` to translate database rows into `User` instances.
  - Cleanly decoupled from SQLAlchemy.

---

### `app/infrastructure/db/schema/user_table.py`

- **Purpose**: Defines the structure of the `users` table using SQLAlchemy Core's `Table(...)`.
- **Role**: Maps the application's database schema to SQLAlchemy constructs so SQL can be generated correctly.
- **Notes**:
  - Field names must match actual database column names.
  - Used only in the data access layer, not in domain logic.
  - Enables query construction like `select(users).where(users.c.email == ...)`.

---

### `app/infrastructure/db/cockroach.py`

- **Purpose**: Establishes the connection to the CockroachDB database.
- **Role**: Creates and returns SQLAlchemy `Session` or `engine` objects using configured credentials.
- **Notes**:
  - Central location for connection configuration.
  - Used during application startup to instantiate repository classes.

---

## Application Wiring (`main.py` or similar entrypoint)

At runtime:

1. The application calls into `cockroach.py` to initialize the database connection.
2. A `CockroachUserRepository` instance is created with that session.
3. The repository is referenced only through the `RelationalRepository` interface.
4. This repository instance is passed into services or use cases that depend on it.

### Benefits:

- **Testability**: Mock repositories can be swapped in easily for unit testing.
- **Extensibility**: Adding support for a different database requires only a new subclass of `RelationalRepository`.
- **Maintainability**: Domain logic is cleanly isolated from data access and persistence logic.

---

## Summary

This architecture provides:

- Strong separation between domain, infrastructure, and interface layers.
- Flexibility to change or expand the data backend.
- Type safety and clarity through the use of dataclasses and Core-based SQL expressions.
- A clean, contract-driven design that aligns with modern best practices.
