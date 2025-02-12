# Restoring Minds - AI Prospecting System

## Project Documentation
- [View Project Presentation](https://docs.google.com/presentation/d/1nr6u6IgGZS-Mvy1X0OSlNuj_unJ8xBY1QURU4YmuV6g/edit?usp=sharing)

## Overview
The AI Prospecting System is a multi-agent platform designed to identify, analyze, and engage with fast-growing companies in the DFW area that could benefit from stress management and emotional intelligence training services. The system utilizes CrewAI for agent orchestration, LangChain for AI interactions, Django for the web framework, and Docker for containerized deployment.

## System Architecture

### Technologies Used
- CrewAI: Agent orchestration and task management
- LangChain: Large language model interactions
- Django: Web application framework
- Docker: Containerization and deployment
- Python: Primary programming language

### Agent Components
The system consists of four specialized AI agents:

1. Market Researcher
2. Business Research and Identification Agent
3. Decision-Maker Identifier
4. Outreach Specialist

## Installation

### Prerequisites
- Python 3.10+
- django
- crewai and crewai-tools
- langchain
- Docker and Docker Compose
- Git

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/username/restoring-minds-ai.git
cd restoring-minds-ai
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. Build and run Docker containers:
```bash
sudo docker compose build --no-cache 
sudo docker compose up -d --build
```

## Configuration

### Environment Variables
```
OPENAI_API_KEY=""
DJANGO_SECRET_KEY="
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

### Agent Configuration
Each agent's behavior can be customized in the admin dashboard:


## Usage

### Starting the System
1. Ensure all containers are running:
```bash
docker-compose ps
```

2. Access the web interface:
```
http://localhost:8000
```

## Agent Workflows

### Market Researcher
- Analyzes market trends and competition
- Generates reports on stress management industry
- Monitors pricing and service offerings

### Business Identifier
- Discovers potential clients in DFW area
- Scores and prioritizes prospects
- Maintains company database

### Decision-Maker Identifier
- Finds key contacts within target companies
- Validates contact information
- Updates contact database

### Outreach Specialist
- Creates personalized communication templates
- Prioritizes leads for outreach
- Monitors engagement metrics

## Data Storage

### Database Schema
```
PostgresQL
```

## Monitoring and Maintenance

### Health Checks
- Agent status monitoring
- API endpoint health
- Database connection status
- Redis queue monitoring

### Logging
Logs are stored in `/var/log/image-restoring-minds/`:
- `agent_activities.log`
- `api_requests.log`
- `error.log`


## Troubleshooting

### Common Issues
1. Agent Connection Failures
   - Check API keys
   - Verify network connectivity
   - Review agent logs

2. Database Issues
   - Check connection string
   - Verify PostgreSQL service
   - Review migration status

3. Docker Container Problems
   - Check container logs
   - Verify resource allocation
   - Review network settings
