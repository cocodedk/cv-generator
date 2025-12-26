# Backend Scripts

Utility scripts for database inspection, maintenance, and testing.

## Scripts Overview

All scripts are located in `backend/scripts/` and should be run inside the Docker container:

```bash
docker-compose exec app python backend/scripts/<script_name>.py
```

## Available Scripts

### check_profile_db.py

Checks the state of profile data in the Neo4j database. This script examines Profile nodes, Person nodes, GET_QUERY results, and relationships to help diagnose database issues.

**Usage:**
```bash
docker-compose exec app python backend/scripts/check_profile_db.py
```

**What it checks:**
- Profile nodes existence and timestamps
- Person nodes linked to profiles
- GET_QUERY result completeness
- Relationships between Profile and related nodes

**Structure:**
The script is modularized into focused components in `backend/scripts/check_profile_db/`:
- `profile_nodes.py` - Profile node inspection
- `person_nodes.py` - Person node verification
- `get_query_result.py` - GET_QUERY result validation
- `relationships.py` - Relationship checking

**Example Output:**
```
=== Profile Nodes ===
Found 1 Profile node(s):
  - updated_at: 2024-01-15T10:30:00

=== Person Nodes ===
Profile 2024-01-15T10:30:00:
  Person nodes: 1
  Names: ['John Doe']

=== GET_QUERY Result ===
Profile found: 2024-01-15T10:30:00
Person: {'name': 'John Doe', ...}
Experiences count: 3
Educations count: 2
Skills count: 5

=== Relationships ===
Profile 2024-01-15T10:30:00:
  Person: 1
  Experience: 3
  Education: 2
  Skill: 5
```

### create_profile_from_me.py

Creates a profile in the Neo4j database using data extracted from `docs/me.md`. Includes personal information, work experience, education, and skills.

**Usage:**
```bash
docker-compose exec app python backend/scripts/create_profile_from_me.py
```

**What it does:**
1. Creates a Profile node in Neo4j
2. Creates Person node with personal information
3. Creates Experience nodes with projects
4. Creates Education nodes
5. Creates Skill nodes with categories and levels

If a profile already exists, it will be updated with the new data.

**Structure:**
The script is modularized into focused components in `backend/scripts/create_profile_from_me/`:
- `profile_data.py` - Main function that combines all profile data
- `personal_info.py` - Personal information data
- `experience.py` - Work experience data with projects
- `education.py` - Education data
- `skills.py` - Skills data with categories and levels
- `create.py` - Profile creation logic

**Example Output:**
```
Creating profile from docs/me.md data...
✅ Profile created successfully!
   Name: Babak Bandpey
   Email: babak@cocode.dk
   Experiences: 4
   Education: 2
   Skills: 50
```

### recover_profile.py

Recovers orphaned nodes and links them to a Profile node.

**Usage:**
```bash
docker-compose exec app python backend/scripts/recover_profile.py
```

### clear_database.py

Clears all data from the Neo4j database.

**Usage:**
```bash
docker-compose exec app python backend/scripts/clear_database.py
```

### count_nodes.py

Counts nodes by type in the database.

**Usage:**
```bash
docker-compose exec app python backend/scripts/count_nodes.py
```

### link_orphaned_nodes.py

Links orphaned nodes to existing Profile nodes.

**Usage:**
```bash
docker-compose exec app python backend/scripts/link_orphaned_nodes.py
```
