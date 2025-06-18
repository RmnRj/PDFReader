# PDF Reader with Annotations

## Overview

This is a Streamlit-based PDF reader application that allows users to upload, read, and annotate PDF documents. The application provides functionality for highlighting text, adding comments, generating notes, and managing annotations across different PDF files.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interaction
- **Backend**: Python modules handling PDF processing, annotation management, and note generation
- **Storage**: File-based storage using JSON for annotations and topics
- **Output**: PDF generation for compiled notes using ReportLab

## Key Components

### Core Modules

1. **app.py** - Main Streamlit application entry point
   - Handles UI rendering and user interactions
   - Manages session state for current PDF and annotations
   - Coordinates between different processing modules

2. **pdf_processor.py** - PDF text extraction and processing
   - Uses pdfplumber library for reliable PDF text extraction
   - Implements page-by-page text extraction with caching
   - Provides search functionality across PDF content

3. **annotation_manager.py** - Annotation persistence and management
   - Handles saving/loading of highlights, comments, and notes
   - Manages file-based storage in JSON format
   - Provides clean filename handling for safe file operations

4. **note_generator.py** - PDF note compilation
   - Uses ReportLab to generate formatted PDF notes
   - Creates structured documents from annotations
   - Supports custom styling and formatting

5. **utils.py** - Utility functions
   - Directory creation and management
   - Color scheme definitions for highlights
   - Filename sanitization utilities

### Storage Structure

```
/annotations/     - JSON files storing PDF annotations
/topics/         - JSON files storing topic classifications
/notes_output/   - Generated PDF notes
/temp/          - Temporary file storage
```

## Data Flow

1. **PDF Upload**: User uploads PDF through Streamlit interface
2. **Text Extraction**: PDFProcessor extracts text content page-by-page
3. **Annotation Creation**: Users create highlights, comments, and notes
4. **Persistence**: AnnotationManager saves annotations to JSON files
5. **Note Generation**: NoteGenerator compiles annotations into formatted PDF

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework for the user interface
- **pdfplumber**: PDF text extraction and processing
- **reportlab**: PDF generation for notes output

### Supporting Libraries
- **json**: Annotation data serialization
- **os**: File system operations
- **datetime**: Timestamp management
- **re**: Text processing and filename cleaning

## Deployment Strategy

The application is configured for Replit deployment with:

- **Runtime**: Python 3.11
- **Server**: Streamlit running on port 5000
- **Deployment Target**: Autoscale configuration
- **Dependencies**: Managed via pyproject.toml with uv package manager

The application uses file-based storage, making it suitable for single-user scenarios or small-scale deployments where data persistence across sessions is handled through the file system.

## Changelog

- June 18, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.