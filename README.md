# Order Management System (OMS)

A FastAPI-based Order Management System built as a QA automation portfolio project.

The goal of this project was to gain hands-on experience building and testing a more realistic backend application. Compared to my earlier API projects, this project includes authentication, database relationships, inventory management, order workflows, and a more structured automated testing approach.

The project combines backend development and QA automation by focusing on both application functionality and automated validation of business rules.

---

# Project Overview

This project was designed to move beyond simple CRUD APIs and introduce concepts commonly found in real-world applications.

The application allows users to:

- Create accounts and log in
- Manage products and inventory
- Create and manage orders
- Progress orders through a workflow
- Validate business rules around inventory and order processing

The project also includes an automated test suite that validates API behavior, security, database state changes, and business workflows.

---

# What I Learned

This project provided hands-on experience with:

- Building REST APIs using FastAPI
- Creating relational database models with SQLAlchemy
- Working with SQLite databases
- Implementing JWT authentication
- Writing automated API tests with pytest
- Testing role-based and ownership-based authorization
- Validating business workflows and state transitions
- Using reusable fixtures, factories, and helpers
- Structuring larger automated test suites
- Running automated tests through GitHub Actions

---

# First Frontend Experience

This project also served as my first opportunity to work with frontend development.

While the primary focus of the project was backend API development and QA automation, I created a simple frontend interface to interact with the Order Management System and better understand the full request/response flow between a user interface and a backend API.

Working on the frontend helped me gain experience with:

- Making API requests from a user interface
- Handling authentication flows
- Displaying API responses and errors
- Connecting frontend actions to backend business rules
- Understanding how automated API testing relates to end-user workflows

As someone coming from a Software Support background, this was a valuable introduction to how frontend and backend components work together in a complete application.

---

# Features

## User Authentication

- Create user accounts
- Login using JWT authentication
- Protected routes using bearer tokens
- Role-based access control

### Roles

- User
- Admin

---

## Product Management

- Create products
- Store product pricing
- Track available stock
- Validate product data
- Prevent invalid inventory operations

---

## Order Management

Authenticated users can:

- Create orders
- Add products to orders
- View their orders
- Retrieve order details
- Pay for orders
- Cancel eligible orders

Additional behavior includes:

- Automatic order total calculations
- Product quantity merging when the same item is added multiple times
- Inventory updates as items are added

---

# Order Workflow

The application includes a stateful order lifecycle.

## Order States

```text
CREATED
PAID
SHIPPED
DELIVERED
CANCELLED
```

## Valid Transitions

```text
CREATED → PAID
PAID → SHIPPED
SHIPPED → DELIVERED

CREATED → CANCELLED
PAID → CANCELLED
```

## Business Rules

- Items can only be added while an order is in CREATED status
- Empty orders cannot be paid
- Only PAID orders can be shipped
- Only SHIPPED orders can be delivered
- Delivered orders are considered terminal
- Shipped and delivered orders cannot be cancelled
- Inventory is restored when eligible orders are cancelled
- Duplicate product additions merge into a single order item

---

# Database Design

The application uses SQLite with SQLAlchemy ORM.

## Main Resources

```text
User
 └── Order
      └── Order Item
            └── Product
```

Relationships include:

- Users own Orders
- Orders contain Order Items
- Order Items reference Products
- Products track inventory levels

The database is used to validate business workflows and inventory changes throughout the order lifecycle.

---

# Testing Focus

This project was built with testing as a major focus.

The automated test suite covers:

- Positive API scenarios
- Negative API scenarios
- Authentication testing
- Authorization testing
- Ownership validation
- Inventory validation
- Order workflow testing
- Database state validation
- Business rule validation
- Edge case testing

---

# Testing Organization

To help keep tests maintainable, the test suite uses:

- Fixtures
- Factories
- Helpers
- Assertion utilities
- Workflow test scenarios
- Database validation tests

This structure made it easier to reuse setup logic and keep tests readable as the project grew.

---

# Tech Stack

## Backend

- FastAPI
- SQLite
- SQLAlchemy

## Authentication

- JWT (python-jose)
- Passlib
- bcrypt

## Testing

- pytest
- pytest-cov
- httpx
- Faker

## Quality Tools

- Black
- GitHub Actions

## Language

- Python 3.11+

---

# Project Structure

```text
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
└── services/

tests/
├── api/
├── workflows/
├── db/
├── fixtures/
├── factories/
├── helpers/
└── assertions/
```

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/tnation1392/project3-OMS.git
cd project3-OMS
```

## 2. Create and Activate a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the API

```bash
uvicorn app.main:app --reload
```

## 5. Open the API Docs

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# Running Tests

## Run All Tests

```bash
pytest -v
```

## Run Smoke Tests

```bash
pytest -v -m smoke
```

## Run Workflow Tests

```bash
pytest -v -m workflow
```

## Run Database Validation Tests

```bash
pytest -v -m db
```

## Run Tests with Coverage

```bash
pytest -v --cov=app --cov-report=term-missing
```

---

# CI Quality Checks

GitHub Actions is used to automatically:

- Run formatting checks
- Execute automated tests
- Generate coverage reports
- Validate quality before changes are merged

The goal is to mimic a simple CI workflow similar to what is used on development teams.

---

# Sample Workflow

A simple demo flow for the system:

1. Create a user
2. Log in and obtain a JWT token
3. Create a product
4. Create an order
5. Add products to the order
6. Pay the order
7. Ship the order as an admin
8. Deliver the order as an admin
9. Retrieve order details

---

# Key Testing Scenarios

Some examples of automated tests in the project include:

- Protected routes require authentication
- Users cannot modify another user's order
- Inventory decreases when products are added
- Inventory is restored when eligible orders are cancelled
- Delivered orders cannot be modified
- Duplicate line items merge correctly
- Business workflow transitions follow defined rules

---

# Why I Built This Project

I built this project to continue developing both backend and QA automation skills.

Compared to my previous projects, this application introduced more realistic business workflows, relational database modeling, authentication, inventory management, and workflow validation.

The project helped me gain experience writing automated tests against a stateful application where actions affect both business logic and database state.

---

# Key Learning Outcomes

Some of the most valuable lessons from this project included:

- Working with relational databases and ORM models
- Implementing JWT authentication
- Managing application state through workflows
- Validating inventory and business rules
- Writing reusable automated tests
- Testing database-backed applications
- Organizing larger automation projects
- Using CI tools to automate quality checks

---

# Future Improvements

Potential future improvements include:

- PostgreSQL support
- Docker support
- Additional API contract testing
- Expanded reporting
- Additional workflow scenarios
- Performance and load testing

---

# Author

Created by **Todd Nason** as a QA Automation portfolio project.
