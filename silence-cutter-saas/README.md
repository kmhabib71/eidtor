# Silence Cutter SaaS

Silence Cutter is a SaaS application that automatically detects and removes silent parts from videos, making them more engaging and concise.

## Project Overview

This project consists of two main components:

- A backend API built with FastAPI, Python
- A frontend web application built with Next.js 14+, React, and TypeScript

### Features

- User authentication and authorization
- Video uploading and processing
- Automatic silence detection and removal
- Dashboard with usage statistics
- Subscription management with different tiers (Free, Pro, Enterprise)
- Payment processing integration with Stripe

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.8+)
- MongoDB
- Redis
- FFmpeg

### Installation

#### Backend

```bash
# Clone the repository
git clone https://github.com/yourusername/silence-cutter-saas.git
cd silence-cutter-saas/backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the backend server
uvicorn app.main:app --reload
```

#### Frontend

```bash
# Navigate to the frontend directory
cd silence-cutter-saas/frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

## Project Structure

### Backend

```
backend/
├── app/
│   ├── api/             # API routes
│   ├── core/            # Core configuration
│   ├── db/              # Database models and connection
│   ├── services/        # Business logic
│   ├── tasks/           # Background tasks
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── Dockerfile           # Docker configuration
```

### Frontend

```
frontend/
├── public/              # Static assets
├── src/
│   ├── app/             # Next.js App Router pages and layouts
│   │   ├── layout.tsx   # Root layout
│   │   ├── page.tsx     # Home page
│   │   ├── error.tsx    # Error handling
│   │   ├── loading.tsx  # Loading UI
│   │   └── ...          # Other routes
│   ├── components/      # React components
│   ├── contexts/        # React contexts
│   ├── hooks/           # Custom hooks
│   ├── lib/             # Utility functions
│   ├── styles/          # CSS styles
│   └── types/           # TypeScript type definitions
├── package.json         # Node.js dependencies
├── tsconfig.json        # TypeScript configuration
└── Dockerfile           # Docker configuration
```

## Development

### Backend

The backend is built with FastAPI and uses:

- MongoDB for the database
- JWT for authentication
- Celery for background task processing
- Redis as the message broker for Celery
- FFmpeg for video processing

### Frontend

The frontend is built with Next.js 14+ and uses:

- App Router for routing (new in Next.js 13+)
- React for UI components
- TypeScript for type safety
- TailwindCSS for styling
- SWR for data fetching
- React Context for state management
- Server Components and Client Components

## Deployment

### Docker Compose

The easiest way to deploy the application is using Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# Check the status of the containers
docker-compose ps

# Stop all services
docker-compose down
```

### Manual Deployment

For production deployments, you can:

1. Deploy the backend to a service like Heroku, AWS, or Google Cloud
2. Deploy the frontend to Vercel or Netlify
3. Set up MongoDB Atlas for the database
4. Configure Redis Cloud for the message broker

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FFmpeg](https://ffmpeg.org/) for video processing capabilities
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [TailwindCSS](https://tailwindcss.com/) for styling
- [Stripe](https://stripe.com/) for payment processing
