from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'taskdb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')

def Initialize_database():
    with psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Task_Manager_Table (
                    Id SERIAL PRIMARY KEY,
                    Name VARCHAR(120) NOT NULL,
                    Status VARCHAR(50) DEFAULT 'pending',
                    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()

Initialize_database()

def get_database_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )

def simulate_task(task_id, delay=6):
    def run():
        time.sleep(delay)
        with get_database_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE Task_Manager_Table
                    SET Status = %s, Updated_at = CURRENT_TIMESTAMP
                    WHERE Id = %s;
                ''', ('completed', task_id))
                conn.commit()
    threading.Thread(target=run).start()

@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.get_json()
    Name = data.get('Name')
    if not Name:
        return jsonify({'error': 'Task name is required'}), 400

    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO Task_Manager_Table (Name) VALUES (%s) RETURNING *;', (Name,))
            task = cur.fetchone()
            conn.commit()
            simulate_task(task['id'])  # Fixed: changed from 'Id' to 'id'
            return jsonify(task), 201

@app.route('/list_tasks', methods=['GET'])
def list_tasks():
    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM Task_Manager_Table ORDER BY Created_at DESC;')
            tasks = cur.fetchall()
            return jsonify(tasks)

@app.route('/get_task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM Task_Manager_Table WHERE Id = %s;', (task_id,))
            task = cur.fetchone()
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            return jsonify(task)

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM Task_Manager_Table WHERE Id = %s RETURNING Id;', (task_id,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Task not found'}), 404
            conn.commit()
            return jsonify({'message': f'Task {task_id} deleted successfully'})

@app.route('/update_task_status/<int:task_id>', methods=['PATCH'])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400

    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE Task_Manager_Table
                SET Status = %s, Updated_at = CURRENT_TIMESTAMP
                WHERE Id = %s
                RETURNING *;
            ''', (status, task_id))
            task = cur.fetchone()
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            conn.commit()
            return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True)
