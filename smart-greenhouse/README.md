# Smart Greenhouse

This is a Smart Greenhouse project created for the Design Patterns and Object-Oriented Techniques course.

The goal of Phase 1 is to build the basic structure of the application and make sure the frontend, backend, and database can communicate with each other. More features such as sensors and devices will be added in the later phases.

## Technologies

The project currently uses:

- Python and FastAPI for the backend
- PostgreSQL for the database
- SQLAlchemy for database connection
- Alembic for database migrations
- React and TypeScript for the frontend
- Vite for the frontend development server
- Tailwind CSS for styling
- Docker Compose for running PostgreSQL

## Project Structure

The project is divided into two main parts:

- `backend` - contains the FastAPI application, database connection and Alembic migrations.
- `frontend` - contains the React dashboard and user interface.

The backend is also separated into domain, application, infrastructure and interface layers so that more functionality can be added later without changing the whole project structure.

## Requirements

Before running the project, make sure you have installed:

- Python 3.11 or newer
- Node.js and npm
- Docker Desktop

## First Time Setup

First, start the PostgreSQL database from the project folder:

```bash
docker compose up -d