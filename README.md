# Duvento

## Prerequisites
- Python 3.8+ 
- pip
- Docker
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ananthakrishn04/Duvento.git
cd Duvento
```

### 2. Create Virtual Environment
```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Navigate to Backend Directory
```bash
cd backend
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start Redis using Docker
```bash
# Ensure Docker is running
docker run -d -p 6379:6379 --name redis-server redis
```

### 6. Run Database Migrations
```bash
python manage.py migrate
```

### 7. Start Development Server
```bash
python manage.py runserver
```

## Additional Configuration

### Environment Variables
Create a `.env` file in the `backend` directory with the following variables:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-database-connection-string
REDIS_URL=redis://localhost:6379
```

### Stopping Services
To stop the Redis container:
```bash
docker stop redis-server
docker rm redis-server
```

## Troubleshooting
- Ensure all prerequisites are installed
- Check that Docker is running before starting Redis
- Verify Python and pip versions
- Make sure you're in the virtual environment when installing dependencies

## Notes
- This setup is for development purposes
- Use a production-ready configuration for deployment
```