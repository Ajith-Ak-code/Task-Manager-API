# Unix-Inspired Task Manager API
  This is a simple Flask API that works like a Unix-style Task Manager. You can create, view, update, and delete tasks. Each task runs in the background and completes automatically after a few seconds.

## 🔧 Technologies Used

- Python
- Flask
- PostgreSQL
- Psycopg2
- Dotenv
- Threading (for background task simulation)

## 📦 Setup Instructions

1.Install dependencies:
  pip install python,flask,Psycopg2

2.Create a .env file:
  DB_HOST=localhost
  DB_NAME=taskdb
  DB_USER=postgres
  DB_PASS=your_password
  Run the API:


📋 API Endpoints

✅ Create a Task

URL: /create_task
Method: POST

    Body:

    {
      "Name": "Test Task"
    }

📃 List All Tasks

URL: /list_tasks
Method: GET

🔍 Get Task by ID

URL: /get_task/<task_id>
Method: GET

🗑 Delete a Task

URL: /delete_task/<task_id>
Method: DELETE

✏️ Update Task Status

URL: /update_task_status/<task_id>
Method: PATCH

    Body:

    {
      "status": "in-progress"
    }
