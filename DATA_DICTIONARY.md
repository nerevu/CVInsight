# CVInsight Data Dictionary

This document provides a comprehensive overview of all data fields extracted by CVInsight's extractors and plugins.

## Table of Contents
- [Base Extractors](#base-extractors)
- [Unified Plugin Architecture](#unified-plugin-architecture)
- [Field Types and Formats](#field-types-and-formats)
- [Sample Output Structure](#sample-output-structure)

## Base Extractors

### Profile Extractor
Extracts basic personal information from resumes.

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `name` | string | Full name of the candidate | "John Smith" |
| `email` | string | Email address | "john.smith@email.com" |
| `contact_number` | string | Phone number | "+1-555-123-4567" |

### Skills Extractor
Extracts technical and soft skills from resumes.

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `skills` | list[string] | List of identified skills | ["Python", "SQL", "Machine Learning"] |

### Education Extractor
Extracts educational background information.

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `educations` | list[dict] | List of educational experiences | See education object structure below |

#### Education Object Structure
```json
{
  "institution": "University of California, Berkeley",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "start_date": "2018-08-01",
  "end_date": "2022-05-15",
  "gpa": "3.8"
}
```

### Experience Extractor
Extracts work experience information.

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `work_experiences` | list[dict] | List of work experiences | See work experience object structure below |

#### Work Experience Object Structure
```json
{
  "company": "Tech Corp",
  "position": "Software Engineer",
  "start_date": "2022-06-01",
  "end_date": "present",
  "description": "Developed web applications using Python and React",
  "location": "San Francisco, CA"
}
```

### Years of Experience (YoE) Extractor
Calculates total years of work experience.

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `YoE` | string/float | Total years of work experience | "3.5" or 3.5 |

## Unified Plugin Architecture

### Extended Analysis Extractor Plugin (`extended_analysis_extractor`)

A comprehensive unified plugin that combines all custom extraction capabilities into a single, high-performance analysis tool. This plugin replaces four individual extractors (relevant YoE, education stats, work stats, and social extractor) with a single LLM call, reducing API usage by 75% while maintaining full functionality.

#### All Fields Extracted (21 Total)

##### Relevant Years of Experience Fields

| Field Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `all_wyoe` | float | Total years of ALL work experience | 0.0 |
| `all_relevant_wyoe` | float | Total years of RELEVANT work experience based on job description | 0.0 |
| `all_eyoe` | float | Total years of ALL education experience | 0.0 |
| `relevant_eyoe` | float | Total years of RELEVANT education experience based on job description | 0.0 |

##### Education Statistics Fields

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `highest_degree` | string | Highest academic degree obtained or being pursued | "Master of Science" |
| `highest_degree_status` | string | Completion status | "completed", "pursuing", "unknown" |
| `highest_degree_major` | string | Field of study for the highest degree | "Computer Science" |
| `highest_degree_school_prestige` | string | Institution prestige level | "low", "medium", "high" |

##### Work Statistics Fields

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `highest_seniority_level` | string | Highest career level achieved | "junior", "mid-level", "senior", "lead", "manager", "director", "executive", "intern" |
| `primary_position_title` | string | Most common or highest-ranking job title | "Software Engineer" |
| `average_tenure_at_company_years` | float | Average duration spent at each company (in years) | 2.5 |

##### Social Profiles & Contact Information Fields

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `phone_number` | string | Contact phone number (formatted for US numbers) | "1-234-567-8901" |
| `email` | string | Primary email address | "user@example.com" |
| `linkedin_url` | string | LinkedIn profile URL | "https://linkedin.com/in/username" |
| `github_url` | string | GitHub profile URL | "https://github.com/username" |
| `twitter_url` | string | Twitter/X profile URL | "https://twitter.com/username" |
| `facebook_url` | string | Facebook profile URL | "https://facebook.com/username" |
| `instagram_url` | string | Instagram profile URL | "https://instagram.com/username" |
| `stackoverflow_url` | string | Stack Overflow profile URL | "https://stackoverflow.com/users/username" |
| `personal_website_url` | string | Personal website or blog URL | "https://username.dev" |
| `other_links` | list[string] | Array of other relevant social/professional links | ["https://medium.com/@username"] |

#### Key Features

- **Performance Optimized**: Single LLM call replaces 4 separate calls (75% reduction in API usage)
- **Intelligent Analysis**: Job description matching for relevance calculation
- **Degree Mapping**: Automatic degree-to-years mapping using standardized criteria
- **Contact Formatting**: Automatic US phone number formatting
- **Comprehensive Coverage**: All-in-one solution for resume analysis

#### Education-to-Years Mapping

The plugin automatically maps degrees to years of education:

| Degree Type | Completed Years | Pursuing Years |
|-------------|-----------------|----------------|
| Diploma/Certificate | 1.0 | 0.5 |
| Associate's Degree | 2.0 | 1.0 |
| Bachelor's Degree | 4.0 | 2.0 |
| Master's Degree | 6.0 | 3.0 |
| PhD/Doctorate | 8.0 | 7.0 |

#### Relevance Scoring System

**Work Experience Relevance:**
- Fully relevant (exact same role): 100% of time
- Highly relevant (similar role, overlapping skills): ~75% of time  
- Moderately relevant (different role, key skills used): ~50% of time
- Slightly relevant (minimal skill overlap): ~25% of time
- Not relevant (no skill overlap): 0% of time

**Education Relevance:**
- If education field closely matches job requirements: count full years
- If partially relevant: count proportionally (75%, 50%, 25%)
- If not relevant at all: count 0

#### Seniority Level Categories
- **Intern**: Internship positions
- **Junior**: Entry-level positions, 0-2 years experience
- **Mid-level**: Mid-level positions, 3-7 years experience  
- **Senior**: Senior positions, 8-15 years experience
- **Lead**: Technical leadership roles
- **Manager**: People management roles
- **Director**: Department leadership roles
- **Executive**: C-level/VP positions, 15+ years experience

#### Institution Prestige Categories
- **High**: Top-tier universities, Ivy League, renowned technical schools
- **Medium**: Well-known state universities, respected regional institutions
- **Low**: Community colleges, lesser-known institutions, trade schools

## Field Types and Formats

### Data Types
- **string**: Text data
- **float**: Decimal numbers (e.g., 3.5, 2.0)
- **int**: Whole numbers (e.g., 3, 5)
- **list[string]**: Array of text values
- **list[dict]**: Array of objects
- **NaN**: Not a Number (used when data cannot be calculated)
- **None/null**: No value available

### Date Formats
All dates are stored in ISO format: `YYYY-MM-DD`
- Example: "2023-08-15"
- "present" indicates ongoing/current positions

### Special Values
- **NaN**: Used for relevant experience fields when no job description is provided
- **0.0**: Default value for total experience fields
- **None**: Used when calculations cannot be performed

## Sample Output Structure

### Complete Resume Analysis Result
```json
{
  "name": "John Smith",
  "email": "john.smith@email.com",
  "contact_number": "+1-555-123-4567",
  "skills": ["Python", "SQL", "Machine Learning", "Data Analysis"],
  "educations": [
    {
      "institution": "University of California, Berkeley",
      "degree": "Master of Science",
      "field_of_study": "Data Science",
      "start_date": "2020-08-01",
      "end_date": "2022-05-15",
      "gpa": "3.9"
    }
  ],
  "work_experiences": [
    {
      "company": "Tech Corp",
      "position": "Senior Data Analyst",
      "start_date": "2022-06-01",
      "end_date": "present",
      "description": "Lead data analysis projects and machine learning initiatives"
    }
  ],
  "YoE": "3.5",
  
  // Extended Analysis Fields (unified plugin)
  "extended_analysis_extractor_all_wyoe": 3.5,
  "extended_analysis_extractor_all_relevant_wyoe": 2.8,
  "extended_analysis_extractor_all_eyoe": 6.0,
  "extended_analysis_extractor_relevant_eyoe": 6.0,
  "extended_analysis_extractor_highest_degree": "Master of Science",
  "extended_analysis_extractor_highest_degree_status": "completed",
  "extended_analysis_extractor_highest_degree_major": "Data Science",
  "extended_analysis_extractor_highest_degree_school_prestige": "high",
  "extended_analysis_extractor_highest_seniority_level": "senior",
  "extended_analysis_extractor_primary_position_title": "Senior Data Analyst",
  "extended_analysis_extractor_average_tenure_at_company_years": 1.5,
  "extended_analysis_extractor_phone_number": "1-555-123-4567",
  "extended_analysis_extractor_email": "john.smith@email.com",
  "extended_analysis_extractor_linkedin_url": "https://linkedin.com/in/johnsmith",
  "extended_analysis_extractor_github_url": "https://github.com/johnsmith",
  "extended_analysis_extractor_personal_website_url": "https://johnsmith.dev",
  
  // Metadata
  "filename": "john_smith_resume.pdf",
  "parsing_status": "success",
  "processing_time": 12.5,
  "date_of_resume_submission": "2023-08-15",
  "job_description_provided": true
}
```

### CSV Export Field Names
When exported to CSV, the unified plugin data is flattened with the format: `extended_analysis_extractor_{field_name}`

Examples:
- `extended_analysis_extractor_all_wyoe`
- `extended_analysis_extractor_highest_degree`
- `extended_analysis_extractor_highest_seniority_level`
- `extended_analysis_extractor_linkedin_url`
- `extended_analysis_extractor_phone_number`
- `extended_analysis_extractor_email`

## Usage Notes

1. **Job Description Dependency**: The `all_relevant_wyoe` and `relevant_eyoe` fields will be `NaN` if no job description is provided during extraction.

2. **Performance Optimization**: When no job description is provided, the relevant YoE extractor skips expensive LLM calls and returns results quickly.

3. **Date Handling**: For positions marked as "present", provide a `date_of_resume_submission` parameter to accurately calculate current tenure.

4. **Degree Mapping**: Education years are automatically calculated based on degree type and status, even without a job description.

5. **Error Handling**: Failed extractions will have `parsing_status: "failed"` and include an `error` field with details.

## Integration Example

```python
from cvinsight.notebook_utils import initialize_client, parse_single_resume

# Initialize client
client = initialize_client(api_key="your-api-key")

# Parse resume with job description
result = parse_single_resume(
    client=client,
    resume_path="path/to/resume.pdf",
    date_of_resume_submission="2023-08-15",
    job_description="Looking for a Data Analyst with Python and SQL experience..."
)

# Access relevant experience fields
print(f"Total work experience: {result['all_wyoe']} years")
print(f"Relevant work experience: {result['all_relevant_wyoe']} years")
print(f"Total education: {result['all_eyoe']} years")
print(f"Relevant education: {result['relevant_eyoe']} years")
print(f"Total relevant experience: {result['total_relevant_yoe']} years")
```
