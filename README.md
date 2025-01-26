# Gousto Recipe Finder

A full-stack web application that allows users to search recipes and generate PDF recipe cards from Gousto's recipe collection. The application is live at [gousto.vfjr.dev](https://gousto.vfjr.dev).

## Features

- Search recipes by URL, name, or ingredient
- Generate printable A4 PDF recipe cards with detailed instructions and images
- View recipe details including prep time, rating, ingredients, and cooking instructions
- "Surprise Me" feature to discover random recipes
- Responsive design for optimal viewing on all devices
- Backend API with recipe caching for improved performance

## Technical Stack

### Frontend
- React with TypeScript
- Vite for fast development and building
- React PDF for PDF generation
- Fuse.js for fuzzy search functionality
- Custom CORS proxy for image handling

### Backend
- FastAPI (Python)
- SQLModel for database ORM
- PostgreSQL for data storage
- Alembic for database migrations
- JWT authentication

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.10 or higher)
- PostgreSQL

### Frontend Setup

1. Clone the repository and navigate to the frontend directory:
   ```sh
   cd frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. Create a `.env.local` file with the required environment variables:
   ```
   VITE_BACKEND_URL=http://localhost:8000
   VITE_CORS_PROXY_URL=your_cors_proxy_url
   VITE_GA_MEASUREMENT_ID=your_ga_id
   ```

4. Start the development server:
   ```sh
   npm run dev
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```

2. Create a `.env` file with the required environment variables:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   FRONTEND_URLS=http://localhost:5173
   SECRET_KEY=your_secret_key
   ```

3. Run database migrations:
   ```sh
   uv run alembic upgrade head
   ```

4. Start the backend server:
   ```sh
   uv run fastapi dev
   ```

Alternatively there is a docker compose file which will start the backend and the postgres database.