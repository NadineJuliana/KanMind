# KanMind Backend

## Description

KanMind Backend is a REST API built with Django and Django REST Framework.

The project provides user authentication, board management, task management and comment functionality for the KanMind application.

Authentication is implemented using Django REST Framework Token Authentication.

---

## Features

* User registration
* User login
* Token authentication
* Board management
* Task management
* Comment management
* Django admin interface

---

## Tech Stack

* Python 3.14
* Django
* Django REST Framework
* DRF Token Authentication
* SQLite3
* django-cors-headers
* python-dotenv

---

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd kanmind-backend
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root based on the provided `.env.template`.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## Database Setup

Apply the migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

---

## Run the Development Server

```bash
python manage.py runserver
```

The server will be available at:

```
http://127.0.0.1:8000/
```

The Django Admin interface is available at:

```
http://127.0.0.1:8000/admin/
```

---

## Authentication

The API uses **Token Authentication**.

After a successful registration or login, the response contains an authentication token.

Include the token in every authenticated request:

```
Authorization: Token <your_token>
```

---

## API Endpoints

### Authentication

| Method | Endpoint             |
| ------ | -------------------- |
| POST   | `/api/registration/` |
| POST   | `/api/login/`        |

### Boards

| Method | Endpoint                  |
| ------ | ------------------------- |
| GET    | `/api/boards/`            |
| POST   | `/api/boards/`            |
| GET    | `/api/boards/{board_id}/` |
| PATCH  | `/api/boards/{board_id}/` |
| DELETE | `/api/boards/{board_id}/` |
| GET    | `/api/email-check/`       |

### Tasks

| Method | Endpoint                     |
| ------ | ---------------------------- |
| GET    | `/api/tasks/assigned-to-me/` |
| GET    | `/api/tasks/reviewing/`      |
| POST   | `/api/tasks/`                |
| GET    | `/api/tasks/{task_id}/`      |
| PATCH  | `/api/tasks/{task_id}/`      |
| DELETE | `/api/tasks/{task_id}/`      |

### Comments

| Method | Endpoint                                      |
| ------ | --------------------------------------------- |
| GET    | `/api/tasks/{task_id}/comments/`              |
| POST   | `/api/tasks/{task_id}/comments/`              |
| DELETE | `/api/tasks/{task_id}/comments/{comment_id}/` |

---

## Project Structure

```
core/
auth_app/
boards_app/
tasks_app/
```

Each application contains its own

* models.py
* admin.py
* api/

  * serializers.py
  * views.py
  * permissions.py
  * urls.py

following Django REST Framework best practices.

---

## Permissions

Authenticated users can:

* create and manage their own boards
* access boards they own or are members of
* create and edit tasks inside accessible boards
* create comments on accessible tasks

Only authorized users are allowed to delete boards, tasks and comments according to the project requirements.

---

## Development Notes

The project follows:

* Django REST Framework Generic Views
* ModelSerializer for CRUD operations
* Token Authentication
* Environment variables using `python-dotenv`
* PEP 8 style guide
* Separation of concerns
* Resource-oriented API design

`django-cors-headers` is configured to allow communication with the provided frontend during development.

---

## Notes

* SQLite is used as the default database.
* The `.env` file is excluded from version control.
* Create your own `.env` file using the provided `.env.template`.
* CORS is configured for local frontend development.

---

## Author

Created as part of a Django REST Framework backend project.
