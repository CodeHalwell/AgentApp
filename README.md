# Agent Document Processing - Code Review Exercise

A monorepo containing a multi-agent document processing pipeline with intentional code issues for code review practice.

## 🏗️ Architecture

### Backend (Python 3.12+)
- **Framework**: Microsoft Agent Framework (`azure-agents`)
- **API**: FastAPI
- **Architecture**: Activity/turn-based multi-agent pipeline

**Agents:**
1. **ClassifierAgent**: Categorizes documents (invoice, receipt, contract, report, other)
2. **ExtractorAgent**: Extracts key information based on document type
3. **RouterAgent**: Routes documents to appropriate downstream systems

### Frontend (Next.js 16 + React 19)
- **Framework**: Next.js 16 with React 19
- **TypeScript**: Strict mode enabled
- **UI Components**: shadcn/ui with Tailwind CSS
- **Features**:
  - Real-time agent status monitoring
  - Live agent logs display
  - Classification results dashboard
  - Document upload interface

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.12+ (for local development)

### Run with Docker Compose

```bash
# Start all services
docker-compose up --build

# Access the applications:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🐛 Code Review Exercise

This codebase contains **intentional issues** for code review practice. Find and document the following types of issues:

### 1. Security Issues
- [ ] Overly permissive CORS configuration
- [ ] Missing input validation
- [ ] Potential injection vulnerabilities
- [ ] Data sanitization gaps

### 2. Error Handling Issues
- [ ] Missing try-catch blocks
- [ ] Unhandled promise rejections
- [ ] No graceful error recovery
- [ ] Silent failures

### 3. Type Safety Issues
- [ ] Usage of `Any` types in Python
- [ ] Missing type annotations
- [ ] Inconsistent typing
- [ ] Poor TypeScript type definitions

### 4. Race Conditions
- [ ] Thread-unsafe shared state in backend
- [ ] Concurrent state updates in frontend
- [ ] Missing synchronization mechanisms
- [ ] Unsafe list/dict operations

## 📝 API Endpoints

### Backend API

- `GET /` - Health check
- `POST /process` - Process a document through the pipeline
  - Upload a `.txt` file
  - Returns classification, extraction, and routing results
- `GET /status` - Get current pipeline status
- `GET /logs` - Get all agent logs
- `GET /results/{task_id}` - Get specific task result

## 🧪 Testing

Create a sample text file to test:

**invoice.txt:**
```
INVOICE #12345
Date: 01/15/2024
Bill To: John Smith
Amount Due: $500.00
Total: $500.00
```

**receipt.txt:**
```
RECEIPT
Store Name: ABC Mart
Date: 01/15/2024
Total: $25.50
Thank you for your purchase!
```

Upload these files through the frontend dashboard or use the API directly:

```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -F "file=@invoice.txt"
```

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base.py          # Agent base class
│   │   │   ├── classifier.py    # Classification agent
│   │   │   ├── extractor.py     # Extraction agent
│   │   │   └── router.py        # Routing agent
│   │   ├── main.py              # FastAPI application
│   │   └── pipeline.py          # Pipeline orchestration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   └── ui/                  # shadcn/ui components
│   ├── lib/
│   │   └── utils.ts             # Utility functions
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
└── docker-compose.yml
```

## 🎯 Code Review Guidelines

When reviewing this code, consider:

1. **Security**: Are there any security vulnerabilities? How would you fix them?
2. **Error Handling**: Where is error handling missing? What could go wrong?
3. **Type Safety**: Where are type annotations missing or incorrect?
4. **Concurrency**: Are there race conditions? How would you prevent them?
5. **Code Quality**: Is the code maintainable? Are there code smells?
6. **Best Practices**: Does the code follow Python/TypeScript/React best practices?

## 🔧 Technologies Used

- **Backend**: Python 3.12, FastAPI, Microsoft Agent Framework (azure-agents), Pydantic
- **Frontend**: Next.js 16, React 19, TypeScript 5, Tailwind CSS, shadcn/ui
- **DevOps**: Docker, Docker Compose

## 📚 Learning Objectives

This exercise helps practice:
- Identifying security vulnerabilities
- Recognizing missing error handling
- Understanding type safety importance
- Detecting race conditions
- Code review skills
- Best practices in modern web development

## 🤝 Contributing

This is a code review exercise. Feel free to:
1. Find all intentional issues
2. Suggest fixes
3. Add tests
4. Improve documentation
5. Enhance the agent pipeline

## 📄 License

MIT License - Feel free to use this for learning and practice.
