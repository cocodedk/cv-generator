# CV Generator Overview

The CV Generator is a full-stack web application for creating professional LibreOffice Writer (.odt) CV documents. It provides a modern React-based interface for inputting CV data and generates formatted documents that can be downloaded and edited.

## Purpose

This application simplifies the CV creation process by:
- Providing an intuitive web form for entering CV information
- Offering a reusable master profile for personal info, experience, and education
- Storing CV data in a Neo4j graph database for easy management
- Generating professional ODT documents with multiple styling themes
- Supporting CRUD operations for managing multiple CVs

## Key Features

- **Web Interface**: Modern React UI with Tailwind CSS for creating and managing CVs
- **ODT Generation**: Generate professional LibreOffice Writer documents
- **CV Storage**: Neo4j graph database for storing and managing CV data
- **CRUD Operations**: Create, read, update, and delete CVs via REST API
- **Search**: Search CVs by name, email, or other criteria
- **Multiple Themes**: Support for different CV styling themes
- **Master Profile**: Save, load, and reuse a single profile across CVs
- **Theme Toggle**: Light/dark mode in the UI
- **Dockerized**: Easy setup with Docker Compose

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: Neo4j 5.15 (graph database)
- **Document Generation**: odfpy library
- **Containerization**: Docker, Docker Compose

## Architecture

The application uses a hybrid development architecture:
- Backend and database run in Docker containers
- Frontend runs locally for optimal development experience
- RESTful API connects frontend and backend

See [Architecture Documentation](../architecture/system-overview.md) for detailed information.
