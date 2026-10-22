# Mini Jira

Mini Jira is a locally run project management app for planning team projects, assigning tasks, tracking work on a board, and discussing tasks. It uses Django REST Framework, SQLite, and a React client.

## Features

- Username/password registration, login, logout, and persistent session authentication
- Private projects with owner/member roles and owner-managed membership
- Four-column task boards, search, status and priority editing, assignment, and due dates
- Task comments with author ownership for editing and deletion
- Database-backed dashboard, task list, and in-app notifications
- Responsive layout for desktop and small screens

## Technology and architecture

- Backend: Python 3.12+, Django 5.2, Django REST Framework, SQLite
- Frontend: React 18, React Router, Axios, Lucide React, Vite
- `backend/config/` owns Django settings and URL routing. `accounts/`, `projects/`, `tasks/`, and `notifications/` hold the API and data models.
- `frontend/src/api/` contains the API client. `frontend/src/App.jsx` contains the page and workflow components; `frontend/src/styles/` contains the responsive styling.

## Data model

- Django `User`: accounts and authentication
- `Project`: owner, name, description, status, start/due dates, timestamps
- `ProjectMembership`: project/user role and join time; unique project/user constraint
- `Task`: project, optional member assignee, creator, status, priority, due date, timestamps
- `Comment`: task, author, content, timestamps
- `Notification`: recipient, actor, type/message, optional related project/task, read state

SQLite data is stored in `backend/db.sqlite3` and survives application restarts.

## API overview

All routes use the `/api/` prefix. Unsafe session-authenticated requests require the CSRF cookie, which the frontend obtains from `/api/auth/csrf/`.

| Area | Routes |
|---|---|
| Authentication | `POST /auth/register/`, `POST /auth/login/`, `POST /auth/logout/`, `GET /auth/me/`, `GET /auth/csrf/` |
| Dashboard | `GET /dashboard/` |
| Projects | `GET/POST /projects/`, `GET/PATCH/DELETE /projects/{id}/`, `GET/POST /projects/{id}/members/`, `DELETE /projects/{id}/members/{user_id}/` |
| Tasks | `GET/POST /tasks/`, `GET/PATCH/DELETE /tasks/{id}/`; filter with `project`, `status`, `priority`, and `search` query parameters |
| Comments | `GET/POST /tasks/{id}/comments/`, `PATCH/DELETE /comments/{id}/` |
| Notifications | `GET /notifications/`, `PATCH /notifications/{id}/`, `POST /notifications/mark-all-read/` |

The API uses Django sessions with CSRF protection. Users can only query projects they own or belong to; owners control project settings and membership. Task assignees must belong to the project. Comment edits/deletes and notification updates are restricted to their owner.

## Install and run (Windows PowerShell)

Run from the repository root (`D:\Mini_jira`).

```powershell
# Optional: recreate the established folder layout in a new checkout
New-Item -ItemType Directory -Force backend, backend\config, backend\accounts, backend\projects, backend\tasks, backend\notifications, frontend, frontend\src, frontend\src\api, frontend\src\components, frontend\src\pages, frontend\src\hooks, frontend\src\styles, frontend\src\utils

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt

Set-Location .\frontend
npm.cmd install
Set-Location ..

Set-Location .\backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is at `http://127.0.0.1:8000`; Django admin is at `http://127.0.0.1:8000/admin/`. In a second PowerShell window, from the repository root:

```powershell
Set-Location .\frontend
npm.cmd run dev
```

The React app is at `http://localhost:5173`. If PowerShell blocks virtual environment activation, run `..\.venv\Scripts\python.exe` (from `backend`) or `\.venv\Scripts\python.exe` (from the repository root) directly.

The Vite development server forwards `/api` requests to Django, keeping browser requests on one origin. If you already had Vite running when changing its proxy configuration, stop it with `Ctrl+C` and start it again.

## Tests and production build

```powershell
Set-Location .\backend
python manage.py test
python manage.py check
Set-Location ..\frontend
npm.cmd run build
```

## Development workflow

1. Start Django and Vite in separate terminals.
2. Register a user in the app. Create a project, then use the Django admin or project membership endpoint to add another user.
3. Create tasks on the board, set their assignees/status/priority/due dates, and discuss each task in its detail modal.
4. Run backend tests after changes to models, permissions, or API behavior; run the Vite production build after frontend changes.

## Configuration and limitations

The local settings use SQLite, `DEBUG=True`, local CORS origins, and a development-only Django key. Before deployment, use environment-provided secrets, disable debug mode, set explicit trusted hosts/origins, and configure HTTPS cookies and a production database. There is no WebSocket transport, deadline scheduler, password reset flow, or production deployment configuration. Project member management is available through the API and Django admin; a dedicated member-management screen is not included yet.
