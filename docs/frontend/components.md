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

**Helper Modules**: `frontend/src/app_helpers/cvForm/`

Main form component for CV data entry. The component has been refactored into smaller, focused modules for maintainability:

- `useKeyboardShortcut.ts`: Custom hook for Ctrl+S / Cmd+S keyboard shortcut handling
- `CVFormModals.tsx`: Component for rendering AI generation and profile loader modals
- `CVFormContent.tsx`: Component for rendering the main form content (header, theme selector, form sections)
- `CVFormLoading.tsx`: Component for displaying loading state while CV data is being loaded
- `useCvLoader.ts`: Hook for loading existing CV data
- `useCvSubmit.ts`: Hook for handling form submission
- `useProfileManager.ts`: Hook for managing profile loading and saving

**Features**:
- React Hook Form integration
- Form validation
- Dynamic array management for experience, education, and skills
- API submission handling
- File download after generation
- Load from Profile button with selective item selection
- Save to Profile button
- Per-field AI Assist in Edit CV mode (rich-text fields)
- Keyboard shortcut support: Ctrl+S (Windows/Linux) or Cmd+S (Mac) to save CV

**Props**:
- `onSuccess`: Callback for successful submission
- `onError`: Callback for errors
- `setLoading`: Loading state setter
- `cvId`: Optional CV ID for edit mode

**Keyboard Shortcuts**:
- **Ctrl+S** (Windows/Linux) or **Cmd+S** (Mac): Saves the CV
  - Prevents browser default save dialog
  - Does not trigger while typing in input fields, textareas, or contenteditable elements
  - Does not trigger while form is loading, submitting, or when modals are open
  - Runs form validation before saving

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

**UX Features**:
- Two "+ Add Skill" buttons for improved usability:
  - One in the header (top-right)
  - One at the bottom (right-aligned) below all skill entries
- Both buttons use the same functionality, allowing users to add skills without scrolling back to the top

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
- Keyboard shortcut support: Ctrl+S (Windows/Linux) or Cmd+S (Mac) to save profile

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
- Keyboard shortcut (Ctrl+S/Cmd+S) for quick saving

**Keyboard Shortcuts**:
- **Ctrl+S** (Windows/Linux) or **Cmd+S** (Mac): Saves the profile
  - Prevents browser default save dialog
  - Does not trigger while typing in input fields or textareas
  - Does not trigger while form is loading or submitting
  - Runs form validation before saving

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

**Helper Modules**: `frontend/src/app_helpers/richTextarea/`

Reusable rich text editor component using TipTap (ProseMirror). The component has been refactored into modular helper files for maintainability:

- `htmlUtils.ts`: HTML utility functions (`stripHtml`, `normalizeHtmlForComparison`)
- `editorConfig.ts`: TipTap editor extensions and props configuration
- `useEditorSync.ts`: Custom hook for syncing editor content with external value prop
- `useAiAssist.ts`: Custom hook for AI assist functionality (rewrite/bullets)
- `AiRewriteModal.tsx`: Modal component for AI rewrite prompt input

**Features**:
- HTML formatting toolbar (bold, italic, underline, strike, headers, lists, links)
- Character counter (counts plain text, excludes HTML tags)
- Max length validation
- Error state styling
- Dark mode support
- Customizable rows/height
- Optional "AI Assist" actions (rewrite/bullets)
- Line break support (Enter and Shift+Enter) with race condition prevention
- List support (bullet lists and ordered lists) - **⚠️ Known issue: lists disappear after save/reload**
- HTML normalization handling for TipTap format differences
- HTML formatting preservation: Formatting (bold, italic, line breaks) is preserved when profiles are reloaded

**AI Assist Features**:
- **AI Rewrite**: Opens a modal to enter a custom prompt, then calls LLM API to rewrite text based on user instruction
- **AI Bullets**: Converts sentences into bullet points using heuristic-based transformations (no LLM required)

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

**AI Rewrite Flow**:
1. User clicks "AI rewrite" button
2. Modal opens with prompt textarea
3. User enters instruction (e.g., "Make it more professional")
4. On submit, calls `/api/ai/rewrite` endpoint
5. LLM response is converted to HTML and inserted into editor
6. Modal closes and editor content is updated

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
