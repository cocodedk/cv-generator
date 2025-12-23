# CV Generation

The CV Generator creates LibreOffice Writer (.odt) documents from CV data using the odfpy library.

## Generation Process

1. **Data Validation**: CV data is validated using Pydantic models
2. **Document Creation**: New OpenDocumentText document is created
3. **Style Application**: Styles are applied based on selected theme
4. **Content Generation**: CV sections are added to the document
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
cv_{first_8_chars_of_cv_id}.odt
```

Example: `cv_a1b2c3d4.odt`

## Output Location

All generated files are saved to:
```
backend/output/
```

## Implementation

The generation logic is in:
- `backend/cv_generator/generator.py`: Main generation class
- `backend/cv_generator/styles.py`: Style definitions
- `backend/cv_generator/template.py`: Template structure

## Customization

To customize CV generation:
1. Modify styles in `backend/cv_generator/styles.py`
2. Adjust layout in `backend/cv_generator/generator.py`
3. Add new themes by extending the style system
