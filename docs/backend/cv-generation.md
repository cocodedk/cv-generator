# CV Generation

The CV Generator creates `.docx` documents from CV data using a Markdown -> Pandoc pipeline.

The system also supports browser-printable HTML output. See [Print HTML Generation](print-html-generation.md) for details.

For pipeline details and template guidance, see [DOCX Generation](docx-generation.md).

## Generation Process

1. **Data Validation**: CV data is validated using Pydantic models
2. **Markdown Rendering**: CV data is rendered into Markdown
3. **Template Selection**: Theme template is selected
4. **DOCX Conversion**: Pandoc converts Markdown into DOCX
5. **File Saving**: Document is saved to `backend/output/` directory

## Supported Themes

- **accented**: Two-column layout with accent colors
- **classic**: Traditional single-column layout
- **colorful**: Vibrant, bright accent colors
- **creative**: Creative/design style with vibrant colors
- **elegant**: Sophisticated, professional design
- **executive**: Refined, conservative executive style
- **minimal**: Simple, minimal styling
- **modern**: Clean, contemporary design
- **professional**: Professional/corporate style with dark navy colors
- **tech**: Tech industry style with modern, green accents

## Document Structure

### Header Section

Contains personal information:
- Name (heading)
- Contact information (email, phone, address, links)
- Professional summary (if provided)

### Experience Section

Lists work experience with:
- Job title and company
- Date range and location
- Short role description
- Related projects (with highlights and tech)

### Education Section

Lists education with:
- Degree and institution
- Year, field of study, and GPA

### Skills Section

Groups skills by category:
- Category headings
- Skill names listed under each category

## File Naming

Generated files follow the pattern:
```
cv_{first_8_chars_of_cv_id}.docx
```

Example: `cv_a1b2c3d4.docx`

## Output Location

All generated files are saved to:
```
backend/output/
```

## Implementation

The generation logic is in:
- `backend/cv_generator_docx/generator.py`: Main DOCX generation class
- `backend/cv_generator_docx/markdown_renderer.py`: Markdown rendering
- `backend/cv_generator_docx/template_builder.py`: Template generation

## Output Formats

The CV Generator supports two output formats:
- **DOCX**: Word-compatible documents (see [DOCX Generation](docx-generation.md))
- **Print HTML**: Browser-printable HTML (see [Print HTML Generation](print-html-generation.md))

## Customization

To customize CV generation:
1. Update templates in `backend/cv_generator_docx/templates/`
2. Adjust Markdown structure in `backend/cv_generator_docx/markdown_renderer.py`
3. Add new themes by extending `backend/themes/`
