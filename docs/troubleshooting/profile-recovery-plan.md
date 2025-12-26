# Profile Recovery Plan

## Current State
- **0 Profile nodes** exist
- **3 orphaned Person nodes** (all "Babak Bandpey", bb@cocode.dk)
- **6 orphaned Experience nodes** (linked to Person nodes but not Profile)
- **8 orphaned Education nodes** (linked to Person nodes but not Profile)
- **13 orphaned Skill nodes** (linked to Person nodes but not Profile)
- **0 Project nodes** (none found)

## Recovery Strategy

### Step 1: Create Profile Node
Create a Profile node with current timestamp:
```cypher
CREATE (profile:Profile { updated_at: datetime() })
RETURN profile
```

### Step 2: Link Primary Person Node
Pick the first orphaned Person node and link it to Profile:
```cypher
MATCH (profile:Profile)
MATCH (person:Person)
WHERE NOT (person)-[:BELONGS_TO_PROFILE]->(:Profile)
WITH profile, person
LIMIT 1
CREATE (person)-[:BELONGS_TO_PROFILE]->(profile)
RETURN person, profile
```

### Step 3: Link All Experience Nodes
Link all Experience nodes (that are linked to any orphaned Person) to Profile:
```cypher
MATCH (profile:Profile)
MATCH (person:Person)-[:HAS_EXPERIENCE]->(exp:Experience)
WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (exp)-[:BELONGS_TO_PROFILE]->(profile)
RETURN count(exp) AS linked_experiences
```

### Step 4: Link All Education Nodes
Link all Education nodes (that are linked to any orphaned Person) to Profile:
```cypher
MATCH (profile:Profile)
MATCH (person:Person)-[:HAS_EDUCATION]->(edu:Education)
WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (edu)-[:BELONGS_TO_PROFILE]->(profile)
RETURN count(edu) AS linked_educations
```

### Step 5: Link All Skill Nodes
Link all Skill nodes (that are linked to any orphaned Person) to Profile:
```cypher
MATCH (profile:Profile)
MATCH (person:Person)-[:HAS_SKILL]->(skill:Skill)
WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (skill)-[:BELONGS_TO_PROFILE]->(profile)
RETURN count(skill) AS linked_skills
```

### Step 6: Link All Project Nodes
Link all Project nodes (that are linked to any Experience) to Profile:
```cypher
MATCH (profile:Profile)
MATCH (exp:Experience)-[:HAS_PROJECT]->(proj:Project)
WHERE (exp)-[:BELONGS_TO_PROFILE]->(profile)
  AND NOT (proj)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (proj)-[:BELONGS_TO_PROFILE]->(profile)
RETURN count(proj) AS linked_projects
```

## Complete Recovery Query

Here's a single transaction that does everything:

```cypher
// Step 1: Create Profile node with current timestamp
CREATE (profile:Profile { updated_at: datetime() })
WITH profile

// Step 2: Link first orphaned Person node to Profile
MATCH (person:Person)
WHERE NOT (person)-[:BELONGS_TO_PROFILE]->(:Profile)
WITH profile, person
LIMIT 1
CREATE (person)-[:BELONGS_TO_PROFILE]->(profile)
WITH profile, person

// Step 3: Link all Experience nodes linked to orphaned Persons
MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)
WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (exp)-[:BELONGS_TO_PROFILE]->(profile)
WITH profile, person

// Step 4: Link all Education nodes linked to orphaned Persons
MATCH (person)-[:HAS_EDUCATION]->(edu:Education)
WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (edu)-[:BELONGS_TO_PROFILE]->(profile)
WITH profile, person

// Step 5: Link all Skill nodes linked to orphaned Persons
MATCH (person)-[:HAS_SKILL]->(skill:Skill)
WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (skill)-[:BELONGS_TO_PROFILE]->(profile)
WITH profile

// Step 6: Link all Project nodes linked to Experiences
MATCH (exp:Experience)-[:HAS_PROJECT]->(proj:Project)
WHERE (exp)-[:BELONGS_TO_PROFILE]->(profile)
  AND NOT (proj)-[:BELONGS_TO_PROFILE]->(:Profile)
CREATE (proj)-[:BELONGS_TO_PROFILE]->(profile)

RETURN profile.updated_at AS profile_updated_at
```

## Verification Query

After recovery, verify everything is connected:

```cypher
MATCH (profile:Profile)
OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
RETURN profile.updated_at AS updated_at,
       count(DISTINCT person) AS persons,
       count(DISTINCT exp) AS experiences,
       count(DISTINCT proj) AS projects,
       count(DISTINCT edu) AS educations,
       count(DISTINCT skill) AS skills
```

## Important Notes

1. **Only ONE Person node will be linked** - The other 2 duplicate Person nodes will remain orphaned (as requested, we're not deleting anything)

2. **All child nodes will be linked** - Even if they're linked to the other orphaned Person nodes, they'll be connected to Profile

3. **Profile timestamp** - Uses `datetime()` which returns ISO format timestamp compatible with the system

4. **Transaction safety** - Run this as a single transaction to ensure atomicity

## Root Cause

The Profile node was deleted (or never created) but child nodes remained. This likely happened because:
- Profile deletion didn't cascade properly
- Profile creation failed but child nodes were created anyway
- Transaction rollback issue where Profile creation rolled back but child creation didn't

## Prevention

After recovery, ensure:
1. Profile node is never deleted without deleting child nodes
2. Profile creation is verified before creating child nodes
3. Transactions are atomic (all or nothing)
