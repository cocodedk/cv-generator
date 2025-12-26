"""Get CV queries - retrieve full CV data."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection
from backend.database.queries.read.queries import build_cv_query
from backend.database.queries.read.process import process_cv_record


def get_cv_by_id(cv_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve CV with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    match_clause = "MATCH (cv:CV {id: $cv_id})"
    query = build_cv_query(match_clause)

    with driver.session(database=database) as session:
        result = session.run(query, cv_id=cv_id)
        record = result.single()
        return process_cv_record(record)


def get_cv_by_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Retrieve CV by filename with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    match_clause = "MATCH (cv:CV {filename: $filename})"
    query = build_cv_query(match_clause)

    with driver.session(database=database) as session:
        result = session.run(query, filename=filename)
        record = result.single()
        return process_cv_record(record)
