"""Check GET_QUERY result."""


def check_get_query_result(session, get_query: str) -> None:
    """Check what GET_QUERY returns.

    Args:
        session: Neo4j database session
        get_query: The GET_QUERY Cypher query string
    """
    print("\n=== GET_QUERY Result ===")
    result = session.run(get_query)
    record = result.single()
    if record:
        print(f"Profile found: {record.get('profile', {}).get('updated_at', 'N/A')}")
        print(f"Person: {record.get('person')}")
        print(
            f"Experiences count: "
            f"{len(record.get('experiences', [])) if record.get('experiences') else 0}"
        )
        print(
            f"Educations count: "
            f"{len(record.get('educations', [])) if record.get('educations') else 0}"
        )
        print(
            f"Skills count: "
            f"{len(record.get('skills', [])) if record.get('skills') else 0}"
        )

        if not record.get("person"):
            print("  ⚠️  NO PERSON NODE IN RESULT!")
    else:
        print("  ⚠️  GET_QUERY returned no results!")
