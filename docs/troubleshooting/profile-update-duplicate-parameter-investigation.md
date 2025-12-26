# Profile Update Duplicate Parameter Error Investigation

## Error Summary

**Error Type**: `TypeError: neo4j._sync.work.transaction.TransactionBase.run() got multiple values for keyword argument 'updated_at'`

**Error Location**:
- `backend/database/queries/profile_update.py:106` in `_create_person_node()`
- Also affects `backend/database/queries/profile_create.py:37` in `_create_person_node()`

**Error Message**:
```
TypeError: neo4j._sync.work.transaction.TransactionBase.run() got multiple values for keyword argument 'updated_at'
```

## Root Cause Analysis

### The Problem

The error occurs because `updated_at` is being passed **twice** to `tx.run()`:

1. **First occurrence**: Explicitly as a keyword argument: `updated_at=updated_at`
2. **Second occurrence**: Inside the `params` dict via `**params` unpacking

### Code Flow

1. **`build_save_params()`** (in `profile_helpers.py:5-27`) includes `updated_at` in the returned params dict:
   ```python
   return {
       "updated_at": updated_at,  # ← updated_at is included here
       "name": personal_info.get("name", ""),
       "title": personal_info.get("title"),
       # ... other params
   }
   ```

2. **`update_profile()`** calls `build_save_params()` and passes the result to `_create_person_node()`:
   ```python
   params = build_save_params(profile_data, updated_at)  # params contains "updated_at"
   _create_person_node(tx, updated_at, params)  # updated_at passed explicitly
   ```

3. **`_create_person_node()`** tries to use both:
   ```python
   tx.run(query, updated_at=updated_at, **params)  # ← ERROR: updated_at passed twice!
   ```
   - `updated_at=updated_at` passes it explicitly
   - `**params` unpacks the dict, which also contains `"updated_at": updated_at`

### Why This Happened

During the refactoring from monolithic queries to helper functions:
- The old monolithic queries used `build_save_params()` which included `updated_at` for the single large query
- The new helper functions need `updated_at` separately to match the Profile node
- The code was updated to pass `updated_at` explicitly but forgot to remove it from `params` before unpacking

### Affected Functions

Both `profile_create.py` and `profile_update.py` have the same issue:

**`profile_create.py:37`**:
```python
def _create_person_node(tx, updated_at: str, params: Dict[str, Any]):
    # ...
    result = tx.run(query, updated_at=updated_at, **params)  # ← Same issue
```

**`profile_update.py:106`**:
```python
def _create_person_node(tx, updated_at: str, params: Dict[str, Any]):
    # ...
    tx.run(query, updated_at=updated_at, **params)  # ← Same issue
```

## How to Fix

### Solution: Remove `updated_at` from params before unpacking

In both `_create_person_node()` functions, exclude `updated_at` from params:

```python
def _create_person_node(tx, updated_at: str, params: Dict[str, Any]):
    """Create Person node and link to Profile."""
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    CREATE (newPerson:Person {
        name: $name,
        # ... rest of query
    })
    CREATE (newPerson)-[:BELONGS_TO_PROFILE]->(profile)
    """
    # Remove updated_at from params since we're passing it explicitly
    params_without_updated_at = {k: v for k, v in params.items() if k != 'updated_at'}
    tx.run(query, updated_at=updated_at, **params_without_updated_at)
```

### Alternative Solution: Don't include `updated_at` in `build_save_params()`

However, this might break other code that expects it. The safer approach is Solution 1.

### Files to Fix

1. `backend/database/queries/profile_create.py` - Line 37
2. `backend/database/queries/profile_update.py` - Line 106

## Prevention

When refactoring queries:
- Check if helper functions receive parameters that are also in unpacked dicts
- Use a helper function to remove duplicate keys before unpacking
- Consider creating separate param builders for different query patterns

## Status

🔴 **UNFIXED** - Needs to be fixed in both `profile_create.py` and `profile_update.py`
