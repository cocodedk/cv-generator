# TypeScript Types

Type definitions for CV data structure and API responses.

## Core Types

### Address
```typescript
interface Address {
  street?: string; city?: string; state?: string; zip?: string; country?: string;
}
```

### PersonalInfo
```typescript
interface PersonalInfo {
  name: string; title?: string; email?: string; phone?: string;
  address?: Address; linkedin?: string; github?: string; website?: string; summary?: string;
}
```

### Experience
```typescript
interface Experience {
  title: string; company: string; start_date: string; end_date?: string;
  description?: string; location?: string;
}
```

### Education
```typescript
interface Education {
  degree: string; institution: string; year?: string; field?: string; gpa?: string;
}
```

### Skill
```typescript
interface Skill {
  name: string; category?: string; level?: string;
}
```

## Composite Types

### CVData
```typescript
interface CVData {
  personal_info: PersonalInfo;
  experience: Experience[];
  education: Education[];
  skills: Skill[];
  theme?: 'classic' | 'modern' | 'minimal' | 'elegant' | 'accented';
}
```

### CVResponse
```typescript
interface CVResponse {
  cv_id: string; filename?: string; status: string;
}
```

### CVListItem
```typescript
interface CVListItem {
  cv_id: string; created_at: string; updated_at: string;
  person_name?: string; filename?: string;
}
```

### CVListResponse
```typescript
interface CVListResponse {
  cvs: CVListItem[]; total: number;
}
```

## Type Location

All types are defined in `frontend/src/types/cv.ts`.

## Type Safety

TypeScript ensures:
- Type checking at compile time
- IntelliSense support in IDEs
- Refactoring safety
- API contract enforcement

## Alignment with Backend

Frontend types mirror backend Pydantic models. See [Backend Models](../backend/models.md) for details.
