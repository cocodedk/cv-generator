# Investigation: 422 Unprocessable Entity on PUT /api/cv/{cv_id}

## Issue Summary

**Error:** `PUT /api/cv/c4c31786-4acb-44a4-a421-02c6b843863a` returns `422 Unprocessable Entity`

**Root Cause:** Schema mismatch between frontend and backend models. The frontend sends `personal_info.title`, but the backend Pydantic model `PersonalInfo` does not accept this field, causing FastAPI validation to reject the request.

## Detailed Analysis

### The Problem

When a PUT request is made to `/api/cv/{cv_id}`, FastAPI validates the request body against the `CVData` Pydantic model. The validation fails because:

1. **Frontend sends `title` field:**
   - Frontend TypeScript type `PersonalInfo` includes `title?: string` (```13:13:frontend/src/types/cv.ts```)
   - Frontend form collects `title` (```37:37:frontend/src/components/PersonalInfo.tsx```)
   - Frontend normalization includes `title` in payload (```25:25:frontend/src/app_helpers/cvForm/normalizeCvData.ts```)

2. **Backend rejects `title` field:**
   - Backend Pydantic model `PersonalInfo` does NOT have a `title` field (```16:33:backend/models.py```)
   - FastAPI validation fails with 422 when unknown fields are present

3. **Inconsistency across codebase:**
   - Backend templates expect `personal_info.title` (```20:21:backend/cv_generator_docx/templates/html/base.html```)
   - Backend markdown renderer uses `personal_info.title` (```22:22:backend/cv_generator_docx/markdown_renderer.py```)
   - Database queries do NOT store/retrieve `title` for Person nodes (```33:69:backend/database/queries/update.py```, ```164:173:backend/database/queries/read.py```)

### Request Flow

```
Frontend (useCvSubmit.ts)
  ↓
normalizeCvDataForApi() includes personal_info.title
  ↓
PUT /api/cv/{cv_id} with payload containing personal_info.title
  ↓
FastAPI validates against CVData model
  ↓
PersonalInfo model validation FAILS (title field not defined)
  ↓
422 Unprocessable Entity
```

### Code Locations

**Frontend (sends `title`):**
- Type definition: `frontend/src/types/cv.ts:13`
- Form component: `frontend/src/components/PersonalInfo.tsx:37`
- Normalization: `frontend/src/app_helpers/cvForm/normalizeCvData.ts:25`

**Backend (missing `title` in model):**
- Pydantic model: `backend/models.py:16-33` (PersonalInfo class)
- Database create: `backend/database/queries/create.py:33-37` (no title in Person node)
- Database update: `backend/database/queries/update.py:33-69` (no title in Person node)
- Database read: `backend/database/queries/read.py:164-173` (no title in response)

**Backend (expects `title`):**
- HTML template: `backend/cv_generator_docx/templates/html/base.html:20-21`
- Print HTML template: `backend/cv_generator_docx/templates/print_html/base.html:32`
- Markdown renderer: `backend/cv_generator_docx/markdown_renderer.py:22`

### Validation Error Details

The error is handled by the validation exception handler (```7:47:backend/app_helpers/exception_handlers.py```), which converts Pydantic validation errors to user-friendly messages. The specific error would be something like:

```json
{
  "detail": ["personal_info.title: extra fields not permitted"],
  "errors": [
    {
      "type": "extra_forbidden",
      "loc": ["body", "personal_info", "title"],
      "msg": "Extra inputs are not permitted"
    }
  ]
}
```

### Impact

- **PUT requests fail** when frontend includes `personal_info.title`
- **Templates may show empty title** even if stored in database (but it's not stored)
- **Data loss** - title field is collected in UI but never persisted
- **Inconsistent behavior** - POST `/api/save-cv` would have the same issue

## Recommended Fix

The `title` field needs to be added to:

1. **Backend Pydantic model** (`backend/models.py`):
   - Add `title: Optional[str] = None` to `PersonalInfo` class

2. **Database queries**:
   - `create.py`: Add `title: $title` to Person node creation
   - `update.py`: Add `title: personal_info.get("title")` to `_create_person_node`
   - `read.py`: Add `"title": person.get("title")` to personal_info dict

3. **Verify consistency**:
   - Ensure all templates handle missing title gracefully (they already do with `{% if %}` checks)

## Related Files

- `backend/app_helpers/routes/cv.py:73-95` - PUT endpoint handler
- `backend/models.py:16-33` - PersonalInfo Pydantic model
- `frontend/src/app_helpers/cvForm/normalizeCvData.ts:22-34` - Normalization function
- `backend/app_helpers/exception_handlers.py:7-47` - Validation error handler
