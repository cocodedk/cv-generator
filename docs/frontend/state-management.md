# State Management

How form state and application state are managed in the CV Generator frontend.

## Form State

### React Hook Form

All forms use **React Hook Form** for state management:

```typescript
const { register, handleSubmit, control, formState: { errors } } = useForm<CVData>()
```

**Benefits**:
- Minimal re-renders
- Built-in validation
- Easy error handling
- Performance optimized

### Form Structure

The main CV form uses nested form structure:

```typescript
{
  personal_info: {
    name: '',
    email: '',
    // ... other fields
  },
  experience: [],
  education: [],
  skills: []
}
```

### Dynamic Arrays

Experience, Education, and Skills use `useFieldArray` for dynamic array management:

```typescript
const { fields, append, remove } = useFieldArray({
  control,
  name: "experience"
})
```

## Application State

### Component-Level State

Most state is managed at component level using React hooks:

- `useState` for local component state
- `useForm` for form state
- `useEffect` for side effects

### Hash-Based Routing

Navigation state is managed via URL hash using `useHashRouting` hook:

**Location**: `frontend/src/app_helpers/useHashRouting.ts`

**View Modes**:
- `form`: New CV form
- `list`: CV list view
- `edit`: Edit existing CV (requires `cvId`)
- `profile`: Profile management
- `profile-list`: Profile list view
- `profile-edit`: Edit existing profile (requires `profileUpdatedAt`)

**Hash Format**:
- `#form` - New CV form
- `#list` - CV list
- `#edit/{cvId}` - Edit CV
- `#profile` - Profile management
- `#profile-list` - Profile list
- `#profile-edit/{updatedAt}` - Edit profile (URL-encoded timestamp)

**URL Encoding**: Profile timestamps are URL-encoded in hash to handle special
characters (e.g., colons in ISO timestamps). The `extractProfileUpdatedAtFromHash`
function automatically decodes them.

**State Synchronization**:
- Initial state is derived from hash on mount
- Hash changes trigger state updates via `hashchange` event listener
- State updates do not modify hash to prevent feedback loops
- Uses ref tracking to prevent state update cycles

### Global State

Currently, there is no global state management library. State is passed via props or managed locally.

**Future Consideration**: For complex state needs, consider:
- Context API for shared state
- Zustand or Redux for complex global state

## Data Flow

### Form Submission Flow

1. User fills form → React Hook Form manages state
2. User submits → `handleSubmit` validates data
3. On valid → `onSubmit` sends API request
4. API response → Success/error callbacks update parent state
5. Parent state → UI updates (notifications, navigation)

### CV List State

1. Component mounts → Fetch CV list from API
2. User searches → Update query, refetch
3. User paginates → Update offset, refetch
4. User deletes → Optimistic update, refetch

## State Persistence

Form data: Not persisted (cleared on submit). CV list: Fetched from API on mount. User preferences: Not stored.

## Loading States

Managed via component-level `isLoading`, parent `setLoading` callback, conditional rendering.

## Error Handling

Multiple levels: Form validation (React Hook Form), API errors (try/catch), global errors (ErrorBoundary).

See [Components](components.md) for details.
