# CV Generation

The CV Generator creates `.docx` documents from CV data using a Markdown -> Pandoc pipeline.

For pipeline details and template guidance, see `docs/backend/docx-generation.md`.

## Generation Process

1. **Data Validation**: CV data is validated using Pydantic models
2. **Markdown Rendering**: CV data is rendered into Markdown
3. **Template Selection**: Theme template is selected
4. **DOCX Conversion**: Pandoc converts Markdown into DOCX
5. **File Saving**: Document is saved to `backend/output/` directory

## Supported Themes

- **classic**: Traditional single-column layout
- **modern**: Clean, contemporary design
- **minimal**: Simple, minimal styling
- **elegant**: Sophisticated, professional design
- **accented**: Two-column layout with accent colors

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
- Job description

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

## Customization

To customize CV generation:
1. Update templates in `backend/cv_generator_docx/templates/`
2. Adjust Markdown structure in `backend/cv_generator_docx/markdown_renderer.py`
3. Add new themes by extending `backend/themes/`
