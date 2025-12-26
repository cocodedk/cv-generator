# Frontend Components

React component structure and usage in the CV Generator frontend.

## Component Hierarchy

```
App
├── Navigation
├── MessageDisplay
├── CVForm
│   ├── PersonalInfo
│   ├── Experience
│   ├── Education
│   └── Skills
├── CVList
└── ProfileManager
    ├── ProfileHeader
    ├── PersonalInfo
    ├── Experience
    ├── Education
    └── Skills
```

## Main Components

### App

**Location**: `frontend/src/App.tsx`

Main application component that manages:
- Hash-based view state (form vs list vs profile)
- Success/error notifications
- Loading states
- Theme toggle state (dark/light)
- Navigation between CV form, CV list, and profile management

**Key Features**:
- View switching via URL hash
- Global message banner via `MessageDisplay`
- Theme toggle wiring for `Navigation`

### CVForm

**Location**: `frontend/src/components/CVForm.tsx`

Main form component for CV data entry.

**Features**:
- React Hook Form integration
- Form validation
- Dynamic array management for experience, education, and skills
- API submission handling
- File download after generation
- Load from Profile button with selective item selection
- Save to Profile button
- Per-field AI Assist in Edit CV mode (rich-text fields)

**Props**:
- `onSuccess`: Callback for successful submission
- `onError`: Callback for errors
- `setLoading`: Loading state setter

### PersonalInfo

**Location**: `frontend/src/components/PersonalInfo.tsx`
Form section: Name (required), Title, Email, Phone, Address components, LinkedIn/GitHub/Website, Summary (rich text editor).

### Experience

**Location**: `frontend/src/components/Experience.tsx`
Dynamic array: Add/remove entries, validation, date handling. Fields: Title, Company (required), Start/End dates, Location, Role Summary (rich text, 300 char limit), Projects (name/description/url/tech/highlights).

### Education

**Location**: `frontend/src/components/Education.tsx`
Dynamic array: Add/remove entries, validation. Fields: Degree, Institution (required), Year, Field, GPA.

### Skills

**Location**: `frontend/src/components/Skills.tsx`
Dynamic array: Add/remove entries, category grouping, level selection. Fields: Name (required), Category, Level.

### CVList

**Location**: `frontend/src/components/CVList.tsx`
Features: Paginated list, search, deletion, editing, file downloads.

### ProfileManager

**Location**: `frontend/src/components/ProfileManager.tsx`

Component for managing the master profile (reusable personal information, experiences, and education).

**Features**:
- React Hook Form integration
- Loads existing profile on mount
- Save/update profile functionality
- Delete profile functionality
- Form validation
- Dynamic array management for experience, education, and skills
- Displays profile status (saved/not saved)
- Per-field AI Assist for rich-text fields (summary, role summary, project highlights)

**Props**:
- `onSuccess`: Callback for successful operations
- `onError`: Callback for errors
- `setLoading`: Loading state setter

**Key Differences from CVForm**:
- No theme selection
- Automatically loads profile data on mount
- Shows "Save Profile" or "Update Profile" based on profile existence
- Includes delete functionality
- AI Assist is always enabled (unlike CVForm where it's only enabled in edit mode)

### Navigation

**Location**: `frontend/src/components/Navigation.tsx`
Top navigation with view switching and a dark/light mode toggle.

### MessageDisplay

**Location**: `frontend/src/components/MessageDisplay.tsx`
Global success/error banner displayed at the top of the page.

### ProfileHeader

**Location**: `frontend/src/components/ProfileHeader.tsx`
Header actions for Profile Manager (reload and delete).

### ErrorBoundary

**Location**: `frontend/src/components/ErrorBoundary.tsx`
React error boundary for graceful error handling.

### RichTextarea

**Location**: `frontend/src/components/RichTextarea.tsx`

Reusable rich text editor component using TipTap (ProseMirror).

**Features**:
- HTML formatting toolbar (bold, italic, underline, strike, headers, lists, links)
- Character counter (counts plain text, excludes HTML tags)
- Max length validation
- Error state styling
- Dark mode support
- Customizable rows/height
- Optional “AI Assist” actions (rewrite/bullets)

**Usage**:
- Personal info summary (4 rows) - used in CVForm and ProfileManager
- Experience descriptions (10 rows, 300 char limit) - used in CVForm and ProfileManager
- Project highlights (3 rows) - used in CVForm and ProfileManager

**Props**:
- `id`: Unique identifier
- `value`: HTML content string
- `onChange`: Callback with HTML content
- `placeholder`: Placeholder text
- `rows`: Number of rows (default: 4)
- `error`: Error object for validation
- `maxLength`: Maximum plain text length
- `className`: Additional CSS classes
- `showAiAssist`: Show AI rewrite/bullets actions (used in Edit CV mode and Profile page)

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
