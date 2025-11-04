# EASM Platform

Modern External Attack Surface Management (EASM) and Vulnerability Management platform built with FastAPI and Nuclei.

## 🎯 Overview

This platform provides three tiers of deployment to match different organizational needs and budgets:

### Tier A - Open Source (Community Edition)
**Perfect for individual security researchers and small teams**

- ✅ Nuclei template management
- ✅ Manual scan triggering
- ✅ Basic vulnerability results view
- ✅ Single user mode
- ✅ SQLite database
- 📦 Free and open source

### Tier B - On-Premise (Business Edition)
**Ideal for medium-sized organizations**

- ✅ Everything in Tier A, plus:
- ✅ Multi-user support with RBAC
- ✅ Scheduled scans
- ✅ Asset inventory management
- ✅ PostgreSQL database
- ✅ Workflow management (New → Investigating → Resolved)
- ✅ Local notifications
- 🏢 Deploy on your infrastructure

### Tier C - Cloud SaaS (Enterprise Edition)
**For organizations requiring scale and advanced features**

- ✅ Everything in Tier B, plus:
- ✅ Multi-tenant architecture
- ✅ Advanced continuous asset discovery
- ✅ Distributed scanning
- ✅ Advanced analytics & reporting
- ✅ API rate limiting & quotas
- ✅ SSO/SAML integration
- ✅ Comprehensive audit logging
- ✅ SLA monitoring
- ☁️ Fully managed cloud service

## 🏗️ Architecture

```
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── workers/     # Celery workers
│   ├── alembic/         # Database migrations
│   └── tests/           # Tests
│
├── frontend/            # SvelteKit frontend
│   └── src/
│       ├── lib/         # Shared utilities
│       ├── routes/      # Pages
│       └── components/  # UI components
│
├── docker/              # Docker configurations
└── docs/                # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Nuclei CLI

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Easm
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set your configuration
```

3. **Choose your tier**

Set `APP_TIER` in `.env`:
- `A` for Open Source
- `B` for On-Premise
- `C` for Cloud SaaS

4. **Start with Docker Compose** (recommended)
```bash
docker-compose up -d
```

Or manually:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Documentation

- [Architecture Guide](docs/architecture.md) (Coming soon)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](docs/deployment.md) (Coming soon)
- [Development Guide](docs/development.md) (Coming soon)

## 🧪 Development

### Run tests
```bash
cd backend
pytest
```

### Database migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🔧 Configuration

Key configuration options in `.env`:

| Variable | Description | Tiers |
|----------|-------------|-------|
| `APP_TIER` | Deployment tier (A/B/C) | All |
| `DATABASE_URL` | Database connection | All |
| `REDIS_URL` | Redis for task queue | B, C |
| `JWT_SECRET_KEY` | JWT token secret | B, C |
| `MULTI_TENANT` | Enable multi-tenancy | C |

## 🛡️ Security

- JWT-based authentication (Tier B/C)
- RBAC with role-based permissions (Tier B/C)
- SSO/SAML support (Tier C)
- Audit logging (Tier C)

## 📊 Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy 2.0 - ORM
- Celery - Task queue
- Redis - Message broker
- PostgreSQL/SQLite - Database
- Nuclei - Vulnerability scanner

**Frontend:**
- SvelteKit - Modern web framework
- Tailwind CSS - Styling
- TypeScript - Type safety

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

## 📄 License

[License TBD]

## 🙏 Acknowledgments

- [Nuclei](https://github.com/projectdiscovery/nuclei) - The vulnerability scanner powering this platform
- All open source contributors

## 📞 Support

- Documentation: [Coming soon]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]

---

**Built with ❤️ for the security community**