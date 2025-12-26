# Database Schema

The CV Generator uses Neo4j graph database to store CV data as nodes and relationships.

## Graph Schema

```mermaid
graph LR
    CV[CV Node] -->|BELONGS_TO_CV| Person[Person Node]
    Person -->|HAS_EXPERIENCE| Exp[Experience Node]
    Exp -->|HAS_PROJECT| Proj[Project Node]
    Person -->|HAS_EDUCATION| Edu[Education Node]
    Person -->|HAS_SKILL| Skill[Skill Node]
    Exp -->|BELONGS_TO_CV| CV
    Proj -->|BELONGS_TO_CV| CV
    Edu -->|BELONGS_TO_CV| CV
    Skill -->|BELONGS_TO_CV| CV
    Profile[Profile Node] -->|BELONGS_TO_PROFILE| Person2[Person Node]
    Person2 -->|HAS_EXPERIENCE| Exp2[Experience Node]
    Exp2 -->|HAS_PROJECT| Proj2[Project Node]
    Person2 -->|HAS_EDUCATION| Edu2[Education Node]
    Person2 -->|HAS_SKILL| Skill2[Skill Node]
    Exp2 -->|BELONGS_TO_PROFILE| Profile
    Proj2 -->|BELONGS_TO_PROFILE| Profile
    Edu2 -->|BELONGS_TO_PROFILE| Profile
    Skill2 -->|BELONGS_TO_PROFILE| Profile
```

## Node Types

### CV Node

**Label**: `CV`

**Properties**:
- `id` (string): Unique CV identifier (UUID)
- `created_at` (string): ISO timestamp
- `updated_at` (string): ISO timestamp
- `filename` (string, optional): Generated DOCX filename
- `theme` (string, optional): CV theme name (classic, modern, minimal, elegant, or accented). Defaults to "classic" if not provided.

### Person Node

**Label**: `Person`

**Properties**:
- `name` (string): Full name
- `email` (string, optional): Email address
- `phone` (string, optional): Phone number
- `address_street`, `address_city`, `address_state`, `address_zip`, `address_country` (string, optional): Address components
- `linkedin` (string, optional): LinkedIn URL
- `github` (string, optional): GitHub URL
- `website` (string, optional): Personal website
- `summary` (string, optional): Professional summary

**Relationships**:
- `BELONGS_TO_CV` → CV node
- `BELONGS_TO_PROFILE` → Profile node (for master profile)
- `BELONGS_TO_PROFILE` → Profile node (for master profile)
- `HAS_EXPERIENCE` → Experience nodes
- `HAS_EDUCATION` → Education nodes
- `HAS_SKILL` → Skill nodes

### Experience Node

**Label**: `Experience`

**Properties**:
- `title` (string): Job title
- `company` (string): Company name
- `start_date` (string): Start date (YYYY-MM)
- `end_date` (string, optional): End date (YYYY-MM or "Present")
- `description` (string, optional): Short role description
- `location` (string, optional): Job location

**Relationships**:
- `BELONGS_TO_CV` → CV node
- `BELONGS_TO_PROFILE` → Profile node (for master profile)
- `HAS_PROJECT` → Project nodes

### Project Node

**Label**: `Project`

**Properties**:
- `name` (string): Project name
- `description` (string, optional): Short project description
- `url` (string, optional): Project URL
- `technologies` (list[string], optional): Technologies used
- `highlights` (list[string], optional): Bullet highlights

**Relationships**:
- `BELONGS_TO_CV` → CV node
- `BELONGS_TO_PROFILE` → Profile node (for master profile)

### Education Node

**Label**: `Education`

**Properties**:
- `degree` (string): Degree name
- `institution` (string): Institution name
- `year` (string, optional): Graduation year
- `field` (string, optional): Field of study
- `gpa` (string, optional): GPA

**Relationships**:
- `BELONGS_TO_CV` → CV node

### Skill Node

**Label**: `Skill`

**Properties**:
- `name` (string): Skill name
- `category` (string, optional): Skill category
- `level` (string, optional): Proficiency level

**Relationships**:
- `BELONGS_TO_CV` → CV node
- `BELONGS_TO_PROFILE` → Profile node (for master profile)

### Profile Node

**Label**: `Profile`

**Properties**:
- `updated_at` (string): ISO timestamp of last update

**Relationships**:
- Connected to Person node via `BELONGS_TO_PROFILE`
- Experience, Education, and Skill nodes connected via `BELONGS_TO_PROFILE`

**Note**: There is only one Profile node per database instance (single master profile). The Profile node does not have an ID since it's unique.

## Query Patterns

- **Create Profile**: Creates Profile node, Person node, and all related nodes with relationships in a single transaction. Implemented in `profile_create/` subfolder:
  - `profile.py` - Profile node creation
  - `person.py` - Person node creation
  - `nodes.py` - Experience, Education, and Skill node creation
  - `create.py` - Main create orchestration function
- **Update Profile**: Updates existing Profile node by deleting old related nodes (Projects, Experiences, Education, Skills, Person) separately to avoid cartesian products, then creates new nodes with updated data. Nodes are deleted in dependency order (Projects → Experiences → Education/Skills → Person). After deletion, verifies all Person nodes were removed (hard-fails if any remain). Creates new Person node and binds all child nodes (Experiences, Education, Skills) to it via `elementId()` to prevent multiplication. Implemented in `profile_update/` subfolder:
  - `delete.py` - Deletion operations (`update_profile_timestamp()`, `delete_profile_nodes()`) and verification (`verify_person_deletion()`, `verify_single_person()`)
  - `person.py` - Person node creation (returns `elementId()`)
  - `experience.py` - Experience node creation (bound to Person via `elementId()`)
  - `education.py` - Education node creation (bound to Person via `elementId()`)
  - `skill.py` - Skill node creation (bound to Person via `elementId()`)
  - `update.py` - Main update orchestration function
- **Read Profile**: Matches Profile node, uses CALL subqueries to traverse relationships and collect all related data, avoiding cartesian products. Implemented in `profile_read/` subfolder:
  - `get.py` - Full profile retrieval (`get_profile()`, `get_profile_by_updated_at()`)
  - `list.py` - Basic profile listing (`list_profiles()`)
  - `queries.py` - Shared query building functions
- **Delete Profile**: Deletes Profile node and all related nodes and relationships. Implemented in `profile_delete/` subfolder:
  - `delete.py` - Deletion operations (`delete_profile()`, `delete_profile_by_updated_at()`)

- **Create CV**: Creates CV node, Person node, and all related nodes with relationships in a single transaction. The implementation makes multiple separate `tx.run()` calls within the transaction (one per node type) for better modularity and maintainability. Implemented in `create/` subfolder:
  - `cv.py` - CV node creation (`create_cv_node()`)
  - `person.py` - Person node creation (`create_person_node()`)
  - `nodes.py` - Experience, Education, and Skill node creation (`create_experience_nodes()`, `create_education_nodes()`, `create_skill_nodes()`)
  - `create.py` - Main create orchestration function (`create_cv()`) - returns CV ID (UUID) directly
- **Read CV**: Matches CV by ID, traverses relationships to collect all related data. Implemented in `read/` subfolder:
  - `get.py` - CV retrieval functions (`get_cv_by_id()`, `get_cv_by_filename()`)
  - `queries.py` - Shared query building functions
  - `process.py` - Record processing functions
- **Update CV**: Deletes old relationships and nodes, creates new ones with updated data. Implemented in `update/` subfolder:
  - `delete.py` - Deletion operations (`update_cv_timestamp()`, `delete_cv_relationships()`)
  - `person.py` - Person node creation
  - `experience.py` - Experience node creation
  - `education.py` - Education node creation
  - `skill.py` - Skill node creation
  - `update.py` - Main update orchestration functions (`update_cv()`, `set_cv_filename()`)
- **Delete CV**: Deletes CV node and all related nodes and relationships. Implemented in `delete.py`.
- **List CVs**: Lists and searches CVs with pagination. Implemented in `list/` subfolder:
  - `list.py` - CV listing with pagination (`list_cvs()`)
  - `search.py` - CV search by skills/experience/education (`search_cvs()`)

See `backend/database/queries/` for implementation details. Profile queries are modularized into separate files following the 135-160 line guideline for maintainability.

For detailed flow diagrams, see [Profile Update Flow](profile-update-flow.md).
