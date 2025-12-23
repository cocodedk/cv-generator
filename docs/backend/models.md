# Data Models

Pydantic models used for request/response validation and data structure.

## Core Models

### Address
```python
class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
```

### PersonalInfo
```python
class PersonalInfo(BaseModel):
    name: str  # Required, 1-200 chars
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
```

### Experience
```python
class Experience(BaseModel):
    title: str  # Required, 1-200 chars
    company: str  # Required, 1-200 chars
    start_date: str  # YYYY-MM format
    end_date: Optional[str] = None  # YYYY-MM or "Present"
    description: Optional[str] = None
    location: Optional[str] = None
```

### Education
```python
class Education(BaseModel):
    degree: str  # Required, 1-200 chars
    institution: str  # Required, 1-200 chars
    year: Optional[str] = None
    field: Optional[str] = None
    gpa: Optional[str] = None
```

### Skill
```python
class Skill(BaseModel):
    name: str  # Required, 1-100 chars
    category: Optional[str] = None
    level: Optional[str] = None
```

## Composite Models

### CVData
```python
class CVData(BaseModel):
    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
```

### CVResponse
```python
class CVResponse(BaseModel):
    cv_id: str
    filename: Optional[str] = None
    status: str = "success"
```

### CVListItem
```python
class CVListItem(BaseModel):
    cv_id: str; created_at: str; updated_at: str
    person_name: Optional[str] = None; filename: Optional[str] = None
```

### CVListResponse
```python
class CVListResponse(BaseModel):
    cvs: List[CVListItem]; total: int
```

### ProfileData
```python
class ProfileData(BaseModel):
    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
```

Same structure as `CVData` but used for master profile storage. Does not include `theme` field.

### ProfileResponse
```python
class ProfileResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
```

Response model for profile operations (save, delete).

## Validation

Pydantic validates: required fields, string lengths, email format, types.

**Location**: `backend/models.py` | **Frontend Types**: [Frontend Types](../frontend/types.md)
