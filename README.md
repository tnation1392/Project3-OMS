# Project-3-OMS

A FastAPI-based Order Management System designed to demonstrate realistic QA automation practices, including JWT authentication, relational data modeling, multi-step business workflows, database validation, layered pytest architecture, and GitHub Actions CI.

This project expands beyond basic CRUD API testing by introducing a stateful order lifecycle, ownership and role-based access rules, stock management, cancellation logic, merged line-item behavior, and a more structured automated test strategy.

--- 

## Why This Project Is More Advanced

This is my third QA automation project and was intentionally designed to go beyond my earlier API testing projects.

Compared with my previous projects, this system introduces:

- A relational data model with users, products, orders, and order items
- JWT-based authentication and role-based access control
- Ownership validation for protected order actions
- A stateful order lifecycle (`CREATED`, `PAID`, `SHIPPED`, `DELIVERED`, `CANCELLED`)
- Business rules such as stock reduction, stock restoration, and terminal-state enforcement
- Duplicate item merge behavior inside open orders
- More structured test architecture using fixtures, factories, helpers, assertion utilities, workflow tests, and DB validation tests
- Smarter CI execution with targeted test strategy

---

## Features

### User / Auth
- Create user accounts
- Login with JWT authentication
- Protected routes using bearer tokens
- Role-based access for admin-only fulfillment actions

### Product / Inventory
- Create products with price and stock
- Validate product input
- Prevent invalid stock usage

### Order Management
- Authenticated users can create their own orders
- Users can add items to `CREATED` orders only
- Repeated additions of the same product merge into a single line item
- Order totals are recalculated automatically
- Stock decreases when items are added
- Stock is restored when eligible orders are cancelled

### Order Lifecycle
- `CREATED -> PAID`
- `PAID -> SHIPPED`
- `SHIPPED -> DELIVERED`
- `CREATED / PAID -> CANCELLED`

### Retrieval
- List the current user’s orders
- Retrieve order detail including items
- Support filtered order history behavior (if implemented)

---

## Tech Stack

- Backend: FastAPI
- Database / ORM: SQLite + SQLAlchemy
- Authentication: JWT (`python-jose`)
- Password Hashing: Passlib / bcrypt
- Testing: pytest, pytest-cov
- Test Data: Faker
- Formatting / Quality:** Black
- CI: GitHub Actions

---

## Order Workflow / State Rules

There is a stateful order lifecycle:

- `CREATED`
- `PAID`
- `SHIPPED`
- `DELIVERED`
- `CANCELLED`

### Valid transitions
- `CREATED -> PAID`
- `PAID -> SHIPPED`
- `SHIPPED -> DELIVERED`
- `CREATED -> CANCELLED`
- `PAID -> CANCELLED`

### Business rules
- Items can only be added while an order is `CREATED`
- Empty orders cannot be paid
- Only `PAID` orders can be shipped
- Only `SHIPPED` orders can be delivered
- Delivered orders are treated as terminal
- Shipped or delivered orders cannot be cancelled
- Cancelling eligible orders restores stock
- Adding the same product twice to a `CREATED` order merges quantity into one line item

--- 

## Authentication / Authorization

The API uses JWT-based authentication for protected order routes.

### Roles
- User
  - Can create and manage their own orders
  - Can add items, pay, and cancel their own orders when allowed by workflow rules
- Admin
  - Can perform fulfillment actions such as shipping and delivering orders

### Ownership rules
- Users can only access or modify their own orders
- Admin-only fulfillment endpoints are protected separately from ownership-based user actions

---

## Project Structure

```text
app/
  api/
  core/
  db/
  models/
  schemas/
  services/

tests/
  api/
  workflows/
  db/
  fixtures/
  factories/
  helpers/
  assertions/
```

---

## CI / Quality Checks

GitHub Actions are used to automate validation of the project.

CI currently supports:
- Black formatting checks
- Smoke tests for fast feedback
- Full test suite execution on deeper validation paths
- Coverage reporting and threshold enforcement (if enabled in current workflow)
- Artifact generation for test and coverage outputs

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd project-3-OMS
```

2.**Running a Virtual Environment**
```
python -m venv .venv
.venv\Scripts\activate
```

**3. Install Dependencies**
```
pip install -r requirements.txt
```

**4. Start the Application**
```
uvicorn app.main:app --reload
```

**5. Open API**
Visit:
http://127.0.0.1:8000/docs

**6. Run Tests**

Run Smoke Tests
```
pytest -v -m smoke
```
Run Workflow Tests
```
pytest -v -m workflow
```
Run DB Validation Tests
```
pytest -v -m db
```
Run Tests with Coverage
```
python -m pytest -v --cov=app --cov-config=.coveragerc --cov-report=term-missing
```

---

## Quick Demo Flow

A simple way to demo the system:

1. Create a user
2. Log in and get a JWT token
3. Create a product
4. Create an order
5. Add items to the order
6. Pay the order
7. Ship the order as admin
8. Deliver the order as admin
9. Retrieve order history and detail

---

## Key Testing Scenarios

- Protected routes require valid JWT authentication
- Users cannot modify another user’s order
- Stock decreases when items are added
- Stock restores on eligible cancellation
- Delivered orders are terminal
- Duplicate line-item additions merge quantity
- Notification side effects can be mocked without affecting shipping state

---

## Key QA Automation Skills Demonstrated

This project demonstrates:

- API test design for positive, negative, and workflow scenarios
- JWT-protected endpoint testing
- Role-based and ownership-based authorization testing
- Database validation and business state verification
- State machine / lifecycle testing
- Test isolation with reusable fixtures
- Test data generation with factories
- Workflow readability improvements using helpers and assertion utilities
- CI automation with quality gates