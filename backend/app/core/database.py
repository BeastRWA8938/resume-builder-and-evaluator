import sqlite3
import json
from datetime import datetime
from backend.app.core.config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            analysis_json TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            employment_type TEXT NOT NULL CHECK(employment_type IN ('Full-time', 'Contract', 'Part-time', 'Internship'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experience_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            repository_url TEXT,
            FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE SET NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            action_taken TEXT NOT NULL,
            outcome_metric TEXT,
            raw_bullet_text TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievement_technologies (
            achievement_id INTEGER NOT NULL,
            tech_name TEXT NOT NULL,
            PRIMARY KEY (achievement_id, tech_name),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievement_skills (
            achievement_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            PRIMARY KEY (achievement_id, skill_name),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issuer TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            expiration_date TEXT,
            verification_url TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution TEXT NOT NULL,
            degree TEXT NOT NULL,
            field_of_study TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            patent_number TEXT NOT NULL UNIQUE,
            issue_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Pending', 'Granted'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            publisher TEXT NOT NULL,
            publication_date TEXT NOT NULL,
            url TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(filename: str, job_title: str, job_description: str, analysis_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    analysis_json = json.dumps(analysis_data)
    
    cursor.execute("""
        INSERT INTO resume_analyses (filename, job_title, job_description, created_at, analysis_json)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, job_title, job_description, created_at, analysis_json))
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_analyses_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, job_title, created_at, analysis_json 
        FROM resume_analyses 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "filename": row["filename"],
            "job_title": row["job_title"],
            "created_at": row["created_at"],
            "result": json.loads(row["analysis_json"])
        })
    return history

def get_analysis(analysis_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, job_title, job_description, created_at, analysis_json 
        FROM resume_analyses 
        WHERE id = ?
    """, (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "filename": row["filename"],
            "job_title": row["job_title"],
            "job_description": row["job_description"],
            "created_at": row["created_at"],
            "result": json.loads(row["analysis_json"])
        }
    return None

def delete_analysis_record(analysis_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resume_analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def save_project(project_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        project_id = project_data.get("id")
        if project_id:
            cursor.execute("""
                UPDATE projects 
                SET experience_id = ?, title = ?, description = ?, repository_url = ?
                WHERE id = ?
            """, (project_data.get("experience_id"), project_data["title"], project_data["description"], project_data.get("repository_url"), project_id))
            cursor.execute("DELETE FROM achievements WHERE project_id = ?", (project_id,))
        else:
            cursor.execute("""
                INSERT INTO projects (experience_id, title, description, repository_url)
                VALUES (?, ?, ?, ?)
            """, (project_data.get("experience_id"), project_data["title"], project_data["description"], project_data.get("repository_url")))
            project_id = cursor.lastrowid
        
        for idx, ach in enumerate(project_data.get("achievements", [])):
            action = ach["action_taken"]
            outcome = ach.get("outcome_metric")
            raw_text = ach["raw_bullet_text"]
            order = ach.get("display_order", idx)
            
            cursor.execute("""
                INSERT INTO achievements (project_id, action_taken, outcome_metric, raw_bullet_text, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, action, outcome, raw_text, order))
            ach_id = cursor.lastrowid
            
            for tech in ach.get("technologies", []):
                cursor.execute("""
                    INSERT OR IGNORE INTO achievement_technologies (achievement_id, tech_name)
                    VALUES (?, ?)
                """, (ach_id, tech))
                
            for skill in ach.get("skills", []):
                cursor.execute("""
                    INSERT OR IGNORE INTO achievement_skills (achievement_id, skill_name)
                    VALUES (?, ?)
                """, (ach_id, skill))
        
        conn.commit()
        return project_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_experience(exp_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        exp_id = exp_data.get("id")
        if exp_id:
            cursor.execute("""
                UPDATE experiences 
                SET company_name = ?, role_title = ?, start_date = ?, end_date = ?, employment_type = ?
                WHERE id = ?
            """, (exp_data["company_name"], exp_data["role_title"], exp_data["start_date"], exp_data.get("end_date"), exp_data["employment_type"], exp_id))
        else:
            cursor.execute("""
                INSERT INTO experiences (company_name, role_title, start_date, end_date, employment_type)
                VALUES (?, ?, ?, ?, ?)
            """, (exp_data["company_name"], exp_data["role_title"], exp_data["start_date"], exp_data.get("end_date"), exp_data["employment_type"]))
            exp_id = cursor.lastrowid
        conn.commit()
        return exp_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, experience_id, title, description, repository_url FROM projects ORDER BY id DESC")
    project_rows = cursor.fetchall()
    projects = []
    for p_row in project_rows:
        proj = dict(p_row)
        cursor.execute("SELECT id, action_taken, outcome_metric, raw_bullet_text, display_order FROM achievements WHERE project_id = ? ORDER BY display_order ASC", (proj["id"],))
        ach_rows = cursor.fetchall()
        achievements = []
        for a_row in ach_rows:
            ach = dict(a_row)
            cursor.execute("SELECT tech_name FROM achievement_technologies WHERE achievement_id = ?", (ach["id"],))
            ach["technologies"] = [t["tech_name"] for t in cursor.fetchall()]
            cursor.execute("SELECT skill_name FROM achievement_skills WHERE achievement_id = ?", (ach["id"],))
            ach["skills"] = [s["skill_name"] for s in cursor.fetchall()]
            achievements.append(ach)
        proj["achievements"] = achievements
        projects.append(proj)
    conn.close()
    return projects

def get_experiences():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name, role_title, start_date, end_date, employment_type FROM experiences ORDER BY start_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_project(project_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_experience(experience_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM experiences WHERE id = ?", (experience_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

