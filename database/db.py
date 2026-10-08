import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.assessment import Assessment


SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 10),
    academic_workload TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    satisfaction TEXT NOT NULL,
    motivation TEXT NOT NULL,
    text_response TEXT NOT NULL,
    text_polarity TEXT NOT NULL CHECK (text_polarity IN ('positive', 'neutral', 'negative')),
    text_score INTEGER NOT NULL CHECK (text_score BETWEEN 0 AND 2),
    positive_terms TEXT NOT NULL DEFAULT '[]',
    negative_terms TEXT NOT NULL DEFAULT '[]',
    contextual_score INTEGER NOT NULL CHECK (contextual_score BETWEEN 0 AND 8),
    total_score INTEGER NOT NULL CHECK (total_score BETWEEN 0 AND 10),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Baixo', 'Médio', 'Alto')),
    expected_risk TEXT,
    is_simulated INTEGER NOT NULL DEFAULT 0 CHECK (is_simulated IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assessments_course ON assessments(course);
CREATE INDEX IF NOT EXISTS idx_assessments_semester ON assessments(semester);
CREATE INDEX IF NOT EXISTS idx_assessments_risk ON assessments(risk_level);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at);
"""

RISK_LEVELS = ('Baixo', 'Médio', 'Alto')
POLARITIES = ('positive', 'neutral', 'negative')


def get_connection(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path: str) -> None:
    """Create the SQLite schema and the indexes when they do not exist."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    with get_connection(database_path) as connection:
        connection.executescript(SCHEMA)


def count_assessments(database_path: str) -> int:
    with get_connection(database_path) as connection:
        row = connection.execute('SELECT COUNT(*) AS total FROM assessments').fetchone()
    return int(row['total'])


def insert_assessment(database_path: str, assessment: Assessment) -> int:
    """Persist an assessment and return its generated identifier."""
    created_at = assessment.created_at or datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    parameters = assessment.to_database_params(created_at)

    statement = """
        INSERT INTO assessments (
            course, semester, academic_workload, difficulty, satisfaction, motivation,
            text_response, text_polarity, text_score, positive_terms, negative_terms,
            contextual_score, total_score, risk_level, expected_risk, is_simulated, created_at
        ) VALUES (
            :course, :semester, :academic_workload, :difficulty, :satisfaction, :motivation,
            :text_response, :text_polarity, :text_score, :positive_terms, :negative_terms,
            :contextual_score, :total_score, :risk_level, :expected_risk, :is_simulated, :created_at
        )
    """
    with get_connection(database_path) as connection:
        cursor = connection.execute(statement, parameters)
        assessment_id = int(cursor.lastrowid)
    return assessment_id


def get_assessment_by_id(database_path: str, assessment_id: int) -> Assessment | None:
    with get_connection(database_path) as connection:
        row = connection.execute(
            'SELECT * FROM assessments WHERE id = ?', (assessment_id,)
        ).fetchone()
    return Assessment.from_row(row) if row else None


def list_assessments(
    database_path: str,
    filters: dict[str, str] | None = None,
    limit: int | None = None,
) -> list[Assessment]:
    """List assessments with safe optional filters for the history screens."""
    filters = filters or {}
    clauses: list[str] = []
    values: list[Any] = []

    search = filters.get('search', '').strip()
    if search:
        clauses.append('(CAST(id AS TEXT) LIKE ? OR course LIKE ? OR text_response LIKE ?)')
        pattern = f'%{search}%'
        values.extend((pattern, pattern, pattern))
    if filters.get('course'):
        clauses.append('course = ?')
        values.append(filters['course'])
    if filters.get('semester'):
        clauses.append('semester = ?')
        values.append(int(filters['semester']))
    if filters.get('risk_level'):
        clauses.append('risk_level = ?')
        values.append(filters['risk_level'])
    if filters.get('simulated_only') == '1':
        clauses.append('is_simulated = 1')

    query = 'SELECT * FROM assessments'
    if clauses:
        query += ' WHERE ' + ' AND '.join(clauses)
    query += ' ORDER BY datetime(created_at) DESC, id DESC'
    if limit is not None:
        query += ' LIMIT ?'
        values.append(limit)

    with get_connection(database_path) as connection:
        rows = connection.execute(query, values).fetchall()
    return [Assessment.from_row(row) for row in rows]


def get_distinct_courses(database_path: str) -> list[str]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            'SELECT DISTINCT course FROM assessments ORDER BY course ASC'
        ).fetchall()
    return [str(row['course']) for row in rows]


def get_dashboard_metrics(database_path: str) -> dict[str, Any]:
    """Return complete aggregations consumed by dashboard, reports and JSON API."""
    metrics: dict[str, Any] = {
        'total': 0,
        'simulated_total': 0,
        'risk_counts': {level: 0 for level in RISK_LEVELS},
        'polarity_counts': {polarity: 0 for polarity in POLARITIES},
        'course_distribution': {'courses': [], 'series': {level: [] for level in RISK_LEVELS}},
        'semester_distribution': {'labels': list(range(1, 11)), 'values': [0] * 10},
        'recent_assessments': [],
    }

    with get_connection(database_path) as connection:
        totals = connection.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN is_simulated = 1 THEN 1 ELSE 0 END) AS simulated_total
            FROM assessments
            """
        ).fetchone()
        metrics['total'] = int(totals['total'] or 0)
        metrics['simulated_total'] = int(totals['simulated_total'] or 0)

        for row in connection.execute(
            'SELECT risk_level, COUNT(*) AS total FROM assessments GROUP BY risk_level'
        ):
            metrics['risk_counts'][row['risk_level']] = int(row['total'])

        for row in connection.execute(
            'SELECT text_polarity, COUNT(*) AS total FROM assessments GROUP BY text_polarity'
        ):
            metrics['polarity_counts'][row['text_polarity']] = int(row['total'])

        course_rows = connection.execute(
            """
            SELECT course, risk_level, COUNT(*) AS total
            FROM assessments
            GROUP BY course, risk_level
            ORDER BY course ASC
            """
        ).fetchall()
        course_totals: dict[str, dict[str, int]] = defaultdict(
            lambda: {level: 0 for level in RISK_LEVELS}
        )
        for row in course_rows:
            course_totals[row['course']][row['risk_level']] = int(row['total'])
        metrics['course_distribution']['courses'] = list(course_totals.keys())
        for level in RISK_LEVELS:
            metrics['course_distribution']['series'][level] = [
                course_totals[course][level] for course in course_totals
            ]

        semester_rows = connection.execute(
            'SELECT semester, COUNT(*) AS total FROM assessments GROUP BY semester'
        ).fetchall()
        for row in semester_rows:
            metrics['semester_distribution']['values'][int(row['semester']) - 1] = int(row['total'])

        recent_rows = connection.execute(
            'SELECT * FROM assessments ORDER BY datetime(created_at) DESC, id DESC LIMIT 5'
        ).fetchall()
        metrics['recent_assessments'] = [Assessment.from_row(row) for row in recent_rows]

    return metrics


def get_validation_assessments(database_path: str) -> list[Assessment]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM assessments
            WHERE expected_risk IS NOT NULL
            ORDER BY id ASC
            """
        ).fetchall()
    return [Assessment.from_row(row) for row in rows]


def delete_simulated_assessments(database_path: str) -> int:
    with get_connection(database_path) as connection:
        cursor = connection.execute('DELETE FROM assessments WHERE is_simulated = 1')
        return int(cursor.rowcount)
