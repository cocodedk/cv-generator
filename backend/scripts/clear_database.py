"""Clear all nodes and relationships from Neo4j database."""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, '/app')

from backend.database.connection import Neo4jConnection


def clear_database():
    """Delete all nodes and relationships from the database."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    # Query to delete all nodes and relationships
    clear_query = """
    MATCH (n)
    DETACH DELETE n
    RETURN count(n) AS deleted_nodes
    """

    # Count before deletion
    count_query = """
    MATCH (n)
    RETURN count(n) AS total_nodes
    """

    with driver.session(database=database) as session:
        print("=== Database Clear Operation ===")

        # Count nodes before deletion
        result = session.run(count_query)
        before_count = result.single()["total_nodes"]
        print(f"Nodes before deletion: {before_count}")

        if before_count == 0:
            print("✅ Database is already empty.")
            return

        # Confirm deletion
        print(f"\n⚠️  WARNING: This will delete ALL {before_count} nodes and relationships!")
        print("Proceeding with deletion...")

        # Delete all nodes
        result = session.run(clear_query)
        deleted_count = result.single()["deleted_nodes"]

        print(f"\n✅ Deleted {deleted_count} nodes")

        # Verify deletion
        result = session.run(count_query)
        after_count = result.single()["total_nodes"]

        if after_count == 0:
            print("✅ Database cleared successfully!")
        else:
            print(f"⚠️  Warning: {after_count} nodes still remain")


if __name__ == "__main__":
    try:
        clear_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        Neo4jConnection.close()
