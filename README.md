# Research Paper Metadata Extractor

A Python pipeline for extracting structured metadata from academic
AI research papers in PDF format.

## Objectives

- Extract paper titles, authors, abstracts, and publication dates.
- Identify official, author-provided GitHub repositories.
- Extract models and datasets used in experiments.
- Capture quantitative benchmark claims.
- Validate and export the results as JSON.

## Status

Project scaffold created. Extraction functionality is under development.

## Setup

Python 3.11 is recommended.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt