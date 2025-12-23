# Frontend Components

React component structure and usage in the CV Generator frontend.

## Component Hierarchy

```
App
├── CVForm
│   ├── PersonalInfo
│   ├── Experience
│   ├── Education
│   └── Skills
└── CVList
```

## Main Components

### App

**Location**: `frontend/src/App.tsx`

Main application component that manages:
- Current view state (form vs list)
- Success/error notifications
- Loading states
- Navigation between CV form and CV list

**Key Features**:
- Error boundary integration
- Toast notifications for user feedback
- View switching logic

### CVForm

**Location**: `frontend/src/components/CVForm.tsx`

Main form component for CV data entry.

**Features**:
- React Hook Form integration
- Form validation
- Dynamic array management for experience, education, and skills
- API submission handling
- File download after generation

**Props**:
- `onSuccess`: Callback for successful submission
- `onError`: Callback for errors
- `setLoading`: Loading state setter

### PersonalInfo

**Location**: `frontend/src/components/PersonalInfo.tsx`
Form section: Name (required), Title, Email, Phone, Address components, LinkedIn/GitHub/Website, Summary.

### Experience

**Location**: `frontend/src/components/Experience.tsx`
Dynamic array: Add/remove entries, validation, date handling. Fields: Title, Company (required), Start/End dates, Location, Description.

### Education

**Location**: `frontend/src/components/Education.tsx`
Dynamic array: Add/remove entries, validation. Fields: Degree, Institution (required), Year, Field, GPA.

### Skills

**Location**: `frontend/src/components/Skills.tsx`
Dynamic array: Add/remove entries, category grouping, level selection. Fields: Name (required), Category, Level.

### CVList

**Location**: `frontend/src/components/CVList.tsx`
Features: Paginated list, search, deletion, editing, file downloads.

### ErrorBoundary

**Location**: `frontend/src/components/ErrorBoundary.tsx`
React error boundary for graceful error handling.

## Form Management

All forms use **React Hook Form** for:
- Form state management
- Validation
- Error handling
- Performance optimization

See [State Management](state-management.md) for details on form state handling.

## Styling

Components use **Tailwind CSS** for styling:
- Utility-first CSS classes
- Responsive design
- Consistent design system
