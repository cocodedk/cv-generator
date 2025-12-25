import { useEffect, useRef } from 'react'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'

interface RichTextareaProps {
  id: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
  error?: { message?: string }
  maxLength?: number
  className?: string
}

// Helper to strip HTML and get plain text
export function stripHtml(html: string): string {
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

export default function RichTextarea({
  id,
  value,
  onChange,
  placeholder,
  rows = 4,
  error,
  maxLength,
  className = '',
}: RichTextareaProps) {
  const quillRef = useRef<ReactQuill>(null)

  // Calculate height based on rows
  const minHeight = rows * 24 // Approximate line height

  const modules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ list: 'ordered' }, { list: 'bullet' }],
      ['link'],
      ['clean'],
    ],
  }

  const formats = ['header', 'bold', 'italic', 'underline', 'strike', 'list', 'bullet', 'link']

  const handleChange = (content: string) => {
    // Strip HTML tags to get plain text length for validation
    const textLength = stripHtml(content).length
    if (maxLength && textLength > maxLength) {
      return // Don't update if exceeds max length
    }
    onChange(content)
  }

  const textLength = stripHtml(value || '').length

  // Custom styles for dark mode
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      .ql-editor {
        min-height: ${minHeight}px;
        color: rgb(17, 24, 39);
      }
      .dark .ql-editor {
        color: rgb(243, 244, 246);
      }
      .ql-container {
        font-family: inherit;
        font-size: 0.875rem;
      }
      .ql-toolbar {
        border-top-left-radius: 0.375rem;
        border-top-right-radius: 0.375rem;
        border-color: rgb(209, 213, 219);
        background-color: rgb(249, 250, 251);
      }
      .dark .ql-toolbar {
        border-color: rgb(55, 65, 81);
        background-color: rgb(31, 41, 55);
      }
      .ql-container {
        border-bottom-left-radius: 0.375rem;
        border-bottom-right-radius: 0.375rem;
        border-color: rgb(209, 213, 219);
        background-color: rgb(249, 250, 251);
      }
      .dark .ql-container {
        border-color: rgb(55, 65, 81);
        background-color: rgb(31, 41, 55);
      }
      .ql-editor.ql-blank::before {
        color: rgb(156, 163, 175);
      }
      .dark .ql-editor.ql-blank::before {
        color: rgb(107, 114, 128);
      }
      .ql-snow .ql-stroke {
        stroke: rgb(107, 114, 128);
      }
      .dark .ql-snow .ql-stroke {
        stroke: rgb(156, 163, 175);
      }
      .ql-snow .ql-fill {
        fill: rgb(107, 114, 128);
      }
      .dark .ql-snow .ql-fill {
        fill: rgb(156, 163, 175);
      }
      .ql-snow .ql-picker-label {
        color: rgb(17, 24, 39);
      }
      .dark .ql-snow .ql-picker-label {
        color: rgb(243, 244, 246);
      }
      ${
        error
          ? `
        .ql-container {
          border-color: rgb(239, 68, 68) !important;
        }
        .ql-toolbar {
          border-color: rgb(239, 68, 68) !important;
        }
      `
          : ''
      }
    `
    document.head.appendChild(style)
    return () => {
      document.head.removeChild(style)
    }
  }, [minHeight, error])

  return (
    <div className={className}>
      <div id={id} aria-labelledby={`${id}-label`} role="textbox" aria-multiline="true">
        <ReactQuill
          ref={quillRef}
          theme="snow"
          value={value || ''}
          onChange={handleChange}
          modules={modules}
          formats={formats}
          placeholder={placeholder}
          style={{ minHeight: `${minHeight}px` }}
        />
      </div>
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error.message}</p>}
      {maxLength && (
        <p
          className={`mt-1 text-xs ${textLength > maxLength ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'}`}
        >
          {textLength} / {maxLength} characters
        </p>
      )}
    </div>
  )
}
