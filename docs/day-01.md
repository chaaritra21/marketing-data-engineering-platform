# Day 1 — Python API Ingestion

## Objective

Build a basic API ingestion pipeline using Python.

## Data Source

JSONPlaceholder API:

https://jsonplaceholder.typicode.com/posts

## Pipeline

API
↓
Extract
↓
Validate
↓
Save Raw JSON

## Technologies

- Python
- Requests
- python-dotenv
- JSON
- Git
- GitHub

## Validation Rules

1. API response must be a list.
2. API response must contain at least one record.
3. Every record must contain:
   - userId
   - id
   - title
   - body

## Output

The raw API response is stored in:

Data/Raw/posts.json