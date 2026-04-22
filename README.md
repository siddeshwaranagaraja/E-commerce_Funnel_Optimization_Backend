# E-commerce Funnel Optimization Backend

## Setup

### Local Run
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run: `uvicorn app:app --reload`

### Env File
Create `.env` with:
```
DATABASE_URL=postgresql://user:password@localhost/db
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_api_key
```

### Docker Run
```
docker build -t backend .
docker run -p 8000:8000 backend
```