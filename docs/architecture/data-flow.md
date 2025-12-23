# Data Flow

This document describes how data flows through the CV Generator application for key operations.

## CV Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database
    participant Generator
    participant Filesystem

    User->>Frontend: Enter CV data
    Frontend->>Frontend: Validate form data
    Frontend->>API: POST /api/generate-cv
    API->>API: Validate with Pydantic
    API->>Database: Create CV nodes
    Database-->>API: Return CV ID
    API->>Generator: Generate ODT file
    Generator->>Filesystem: Save .odt file
    Generator-->>API: Return file path
    API->>Database: Store filename
    API-->>Frontend: Return CV ID + filename
    Frontend->>API: GET /api/download/{filename}
    API->>Filesystem: Read file
    API-->>Frontend: Return file
    Frontend->>User: Download file
```

## CV Retrieval Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant Database

    Frontend->>API: GET /api/cv/{cv_id}
    API->>Database: Query CV by ID
    Database-->>API: Return CV data
    API->>API: Transform to response model
    API-->>Frontend: Return CV data
    Frontend->>Frontend: Populate form
```

## CV List Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant Database

    Frontend->>API: GET /api/cvs?limit=50&offset=0&search=name
    API->>Database: Query CV list with filters
    Database-->>API: Return CV list + total count
    API->>API: Format response
    API-->>Frontend: Return paginated list
    Frontend->>Frontend: Display CV list
```

## CV Update Flow

Frontend sends PUT request → API validates → Database deletes old relationships → Creates new nodes → Returns success.

## CV Delete Flow

Frontend sends DELETE request → API deletes CV and relationships from database → Returns success.

## Error Handling

All endpoints: validation errors (400), not found (404), server errors (500). Frontend displays error messages.

See [API Endpoints](../backend/api-endpoints.md) for details.
