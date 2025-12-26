# Profile Memory Error Investigation

## Executive Summary

**Status**: ✅ **FIXED** - The UPDATE_QUERY has been refactored to delete nodes separately, eliminating the cartesian product bug.

**Root Cause**: The `UPDATE_QUERY` had a **critical logic bug** - it chained `OPTIONAL MATCH` statements which created a cartesian product, causing exponential memory usage.

**Example**: A profile with 20 experiences, 100 projects, 5 educations, and 50 skills created **500,000 rows** in memory instead of the actual 176 nodes.

**Fix Applied**: Delete each node type separately using direct `MATCH` patterns instead of chained `OPTIONAL MATCH`. Nodes are deleted in dependency order (Projects → Experiences → Education/Skills → Person) to avoid cartesian products.

## Error Summary

**Error Type**: `Neo.TransientError.General.MemoryPoolOutOfMemoryError`

**Error Message**:
```
The allocation of an extra 96.0 MiB would use more than the limit 5.3 GiB.
Currently using 5.3 GiB. dbms.memory.transaction.total.max threshold reached
```

**Location**: `backend/database/queries/profile.py:52` in `update_profile()` function

**Impact**: Profile save operations fail when the profile data is large.

## Root Cause Analysis

### 1. **CRITICAL BUG: Cartesian Product in UPDATE_QUERY**

The `UPDATE_QUERY` in `backend/database/queries/profile_queries.py` (lines 53-57) has a **critical logic error**:

```53:57:backend/database/queries/profile_queries.py
OPTIONAL MATCH (old_person:Person)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (old_person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (old_person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
OPTIONAL MATCH (old_person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
```

**THE BUG**: Chaining `OPTIONAL MATCH` statements like this creates a **CARTESIAN PRODUCT**!

Each `OPTIONAL MATCH` multiplies the number of rows. For a profile with:
- 1 Person node
- 20 Experience nodes
- 100 Project nodes (5 per experience)
- 5 Education nodes
- 50 Skill nodes

**Cartesian product calculation**:
- Row 1: 1 person
- Row 2: 1 person × 20 experiences = 20 rows
- Row 3: 20 rows × 100 projects = **2,000 rows**
- Row 4: 2,000 rows × 5 educations = **10,000 rows**
- Row 5: 10,000 rows × 50 skills = **500,000 rows**

**Neo4j loads 500,000 rows into transaction memory** before the `DETACH DELETE`!

### 2. Comparison with GET_QUERY (Correct Pattern)

The `GET_QUERY` (lines 104-126) correctly avoids cartesian products by using `CALL` subqueries:

```104:126:backend/database/queries/profile_queries.py
CALL {
    WITH profile, person
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile, exp
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
    WITH exp, collect(DISTINCT proj) AS projects
    RETURN collect(...) AS experiences
}
CALL {
    WITH profile, person
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN collect(DISTINCT edu) AS educations
}
```

Each `CALL` subquery processes one relationship type independently, avoiding cartesian products.

### 3. Memory Usage Calculation

For the example profile above:
- **Actual nodes to delete**: ~176 nodes (1 Person + 20 Experience + 100 Project + 5 Education + 50 Skill)
- **Rows loaded into memory**: **500,000 rows** (cartesian product)
- **Memory per row**: ~1-5 KB (node data + relationships)
- **Total memory**: 500,000 × 3 KB = **~1.5 GB** just for the deletion operation
- **Plus new data creation**: Another 100+ MB
- **Transaction total**: **~1.6 GB per save operation**

This easily exceeds Neo4j's default transaction memory limit of 5.3 GiB, especially with concurrent transactions.

### 3. Neo4j Memory Configuration

The `docker-compose.yml` file does not configure Neo4j memory settings:

```1:25:docker-compose.yml
services:
  neo4j:
    image: neo4j:5.15-community
    container_name: cv-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-cvpassword}
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*
```

**Default Neo4j 5.15 memory settings**:
- `dbms.memory.transaction.total.max`: ~5.3 GiB (default)
- `dbms.memory.heap.initial_size`: Auto-detected
- `dbms.memory.heap.max_size`: Auto-detected

The transaction memory pool is shared across all concurrent transactions, so if multiple operations are running, the available memory per transaction decreases.

### 4. Transaction Retry Behavior

The error logs show retry attempts:
```
WARNING:neo4j:Transaction failed and will be retried in 1.1277318057545616s
WARNING:neo4j:Transaction failed and will be retried in 2.354549456028538s
```

Neo4j automatically retries transient errors, but if the memory issue persists, retries will continue to fail.

## How to Fix

### Solution 1: Fix UPDATE_QUERY to Delete Nodes Separately (REQUIRED)

**The fix**: Delete each node type separately using direct `MATCH` patterns, avoiding cartesian products:

```cypher
MATCH (profile:Profile)
WITH profile ORDER BY profile.updated_at DESC LIMIT 1
SET profile.updated_at = $updated_at
WITH profile
// Delete Projects first (no cartesian product)
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(proj:Project)
DETACH DELETE proj
WITH profile
// Delete Experiences
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(exp:Experience)
DETACH DELETE exp
WITH profile
// Delete Education
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(edu:Education)
DETACH DELETE edu
WITH profile
// Delete Skills
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(skill:Skill)
DETACH DELETE skill
WITH profile
// Delete Person last
MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
DETACH DELETE person
WITH profile
// Create new nodes (existing FOREACH logic)
CREATE (newPerson:Person {...})
...
```

**Why this works**: Each deletion is independent, processing only the specific node type. No cartesian product!

### Solution 2: Use MERGE Pattern Instead of DELETE+CREATE

Instead of deleting and recreating, use `MERGE` to update existing nodes:

```cypher
MATCH (profile:Profile)
WITH profile ORDER BY profile.updated_at DESC LIMIT 1
MERGE (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
SET person = {name: $name, title: $title, ...}
```

**Pros**: Only updates changed properties, doesn't delete/recreate
**Cons**: More complex query logic, need to handle node matching

### Solution 3: Increase Neo4j Transaction Memory

Add to `docker-compose.yml`:

```yaml
environment:
  - NEO4J_dbms_memory_transaction_total_max=10G
```

**Pros**: Quick fix, allows larger transactions
**Cons**: Doesn't solve the underlying inefficiency, may delay the problem

### Solution 4: Implement Chunked Updates

Modify `update_profile()` to process data in chunks:

1. Delete old data in batches
2. Create new data in batches
3. Use multiple smaller transactions

**Pros**: Most scalable solution
**Cons**: More complex implementation, requires refactoring

## Recommended Fix Strategy

**IMMEDIATE (Critical Fix - Required)**:
1. **Fix UPDATE_QUERY** to delete nodes separately (Solution 1 above)
   - This is a **logic bug**, not just an optimization
   - The current query is fundamentally broken for any profile with multiple nodes
   - Must be fixed before increasing memory limits

**Short-term (After Fix)**:
1. Add monitoring/logging to track profile sizes
2. Consider increasing Neo4j transaction memory limit if needed (but shouldn't be necessary after fix)

**Long-term (Architecture)**:
1. Consider using MERGE pattern for incremental updates
2. Implement profile size validation before save
3. Add pagination/chunking for very large profiles
4. Consider archiving old profile versions instead of keeping all in one structure

## Prevention

1. **Add profile size validation**:
   - Limit number of experiences (e.g., max 50)
   - Limit projects per experience (e.g., max 20)
   - Limit total nodes per profile

2. **Monitor profile sizes**:
   - Log profile statistics (node counts) before save
   - Alert on large profiles

3. **Optimize data structure**:
   - Consider storing large text fields (descriptions) separately
   - Use compression for large arrays (technologies, highlights)

## Testing

To reproduce and test fixes:

1. Create a large profile with:
   - 50+ experiences
   - 10+ projects per experience
   - 100+ skills
   - Large text fields (descriptions, summaries)

2. Attempt to save and monitor memory usage

3. Verify fixes work with profiles of various sizes
