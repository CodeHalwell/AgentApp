# Code Review Exercise Guide

This document provides detailed guidance for conducting a code review of this intentionally flawed codebase.

## Overview

This monorepo contains a multi-agent document processing system with **intentionally planted bugs** across four categories:
1. Security vulnerabilities
2. Missing error handling
3. Poor type safety
4. Race conditions

Your task is to find these issues, document them, and propose fixes.

---

## Issue Categories

### 1. Security Issues 🔒

#### Issue #1: Overly Permissive CORS Configuration
**Location**: `backend/app/main.py:14-19`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ SECURITY ISSUE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem**: 
- Allows any origin to access the API
- Combined with `allow_credentials=True`, this is a security risk
- Could enable CSRF attacks

**Fix**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only necessary methods
    allow_headers=["Content-Type"],
)
```

#### Issue #2: Missing Input Validation
**Location**: `backend/app/main.py:25-33`

```python
@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    text = content.decode('utf-8')  # ⚠️ No file size limit
    result = pipeline.process(text)
    return result
```

**Problem**:
- No file size validation (DoS risk)
- No content type validation
- Could crash with large files

**Fix**:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> ProcessResult:
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    
    # Read with size limit
    content = await file.read(MAX_FILE_SIZE)
    if len(content) >= MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid UTF-8 encoding")
    
    result = pipeline.process(text)
    return result
```

#### Issue #3: SQL Injection Risk in task_id
**Location**: `backend/app/main.py:48-52`

```python
@app.get("/results/{task_id}")
async def get_result(task_id: str):
    # ⚠️ No validation on task_id
    result = pipeline.get_result(task_id)
    return result
```

**Problem**:
- If later connected to a database, this could be vulnerable to SQL injection
- No validation of task_id format (should be UUID)

**Fix**:
```python
from uuid import UUID

@app.get("/results/{task_id}")
async def get_result(task_id: str) -> Dict[str, Any]:
    try:
        # Validate UUID format
        uuid_obj = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    result = pipeline.get_result(str(uuid_obj))
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result
```

#### Issue #4: ReDoS (Regular Expression Denial of Service)
**Location**: `backend/app/agents/extractor.py:20-30`

```python
# ⚠️ Potentially vulnerable regex patterns
invoice_match = re.search(r'invoice[:\s#]+(\w+)', text, re.IGNORECASE)
amount_matches = re.findall(r'\$(\d+\.?\d*)', text)
```

**Problem**:
- Unconstrained input could cause catastrophic backtracking
- No timeout on regex operations

**Fix**:
```python
import re
from functools import lru_cache

# Compile patterns once
INVOICE_PATTERN = re.compile(r'invoice[:\s#]+(\w{1,50})', re.IGNORECASE)
AMOUNT_PATTERN = re.compile(r'\$(\d{1,10}\.?\d{0,2})')

# Add input size limits
MAX_TEXT_LENGTH = 100_000

def extract_invoice(text: str) -> Optional[str]:
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    
    match = INVOICE_PATTERN.search(text)
    return match.group(1) if match else None
```

---

### 2. Error Handling Issues 🚨

#### Issue #5: No Try-Catch in API Endpoints
**Location**: `backend/app/main.py:25-52`

```python
@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> Any:
    # ⚠️ No error handling at all
    content = await file.read()
    text = content.decode('utf-8')  # Could raise UnicodeDecodeError
    result = pipeline.process(text)
    return result
```

**Problem**:
- Unhandled exceptions crash the endpoint
- No graceful error messages for clients
- Difficult to debug issues

**Fix**:
```python
@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> ProcessResult:
    try:
        content = await file.read()
        text = content.decode('utf-8')
        result = pipeline.process(text)
        return result
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding")
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing failed")
```

#### Issue #6: Silent Failures in Agents
**Location**: `backend/app/agents/classifier.py:18-42`

```python
def process(self, text: str) -> Dict[str, Any]:
    self.log(f"Classifying document with {len(text)} characters")
    
    # ⚠️ What if text is None or empty?
    text_lower = text.lower()
    # ... classification logic
```

**Problem**:
- No validation of input
- Will crash with None or non-string input
- No error logging

**Fix**:
```python
def process(self, text: str) -> Dict[str, Any]:
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        if len(text) > 1_000_000:
            raise ValueError("Text too long")
        
        self.log(f"Classifying document with {len(text)} characters")
        text_lower = text.lower()
        # ... classification logic
        
    except Exception as e:
        self.log(f"Classification error: {str(e)}", level="error")
        raise
```

#### Issue #7: Unhandled Promise Rejections in Frontend
**Location**: `frontend/app/page.tsx:28-36`

```typescript
const fetchData = async () => {
  // ⚠️ No error handling
  const statusRes = await fetch(`${API_URL}/status`)
  const statusData = await statusRes.json()
  setStatus(statusData)

  const logsRes = await fetch(`${API_URL}/logs`)
  const logsData = await logsRes.json()
  setLogs(logsData)
}
```

**Problem**:
- Network errors are unhandled
- Failed fetches crash the component
- No user feedback on errors

**Fix**:
```typescript
const [error, setError] = useState<string | null>(null)

const fetchData = async () => {
  try {
    const statusRes = await fetch(`${API_URL}/status`)
    if (!statusRes.ok) throw new Error('Failed to fetch status')
    const statusData = await statusRes.json()
    setStatus(statusData)

    const logsRes = await fetch(`${API_URL}/logs`)
    if (!logsRes.ok) throw new Error('Failed to fetch logs')
    const logsData = await logsRes.json()
    setLogs(logsData)
    
    setError(null)
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown error')
    console.error('Fetch error:', err)
  }
}
```

---

### 3. Type Safety Issues 📝

#### Issue #8: Overuse of `Any` Type
**Location**: Multiple files

**Python Examples**:
```python
# backend/app/main.py:25
async def process_document(file: UploadFile = File(...)) -> Any:  # ⚠️

# backend/app/agents/base.py:23
def get_logs(self) -> Any:  # ⚠️

# backend/app/pipeline.py:78
def get_result(self, task_id: str) -> Any:  # ⚠️
```

**TypeScript Examples**:
```typescript
// frontend/app/page.tsx:12-15
const [status, setStatus] = useState<any>(null)  // ⚠️
const [logs, setLogs] = useState<any[]>([])     // ⚠️
const [results, setResults] = useState<any[]>([])  // ⚠️
```

**Problem**:
- Defeats the purpose of type checking
- No IDE autocomplete
- Runtime errors not caught at compile time
- Makes refactoring dangerous

**Fix - Python**:
```python
from typing import List, Dict
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    category: str
    confidence: float
    agent: str

class ExtractionResult(BaseModel):
    extracted_data: Dict[str, Any]
    agent: str

class ProcessResult(BaseModel):
    task_id: str
    classification: ClassificationResult
    extraction: ExtractionResult
    routing: Dict[str, Any]
    status: str
    timestamp: str

# Now use proper types
async def process_document(file: UploadFile = File(...)) -> ProcessResult:
    # ...

def get_logs(self) -> List[Dict[str, str]]:
    # ...
```

**Fix - TypeScript**:
```typescript
interface AgentLog {
  agent: string
  message: string
  level: string
  timestamp: string
}

interface Classification {
  category: string
  confidence: number
  agent: string
}

interface ProcessResult {
  task_id: string
  classification: Classification
  extraction: {
    extracted_data: Record<string, any>
    agent: string
  }
  routing: {
    destination: string
    status: string
  }
  status: string
  timestamp: string
}

interface PipelineStatus {
  active_tasks: number
  completed_tasks: number
  agents: Record<string, string>
}

// Now use proper types
const [status, setStatus] = useState<PipelineStatus | null>(null)
const [logs, setLogs] = useState<AgentLog[]>([])
const [results, setResults] = useState<ProcessResult[]>([])
```

#### Issue #9: Missing Type Annotations
**Location**: `backend/app/agents/base.py:12-13`

```python
def __init__(self, name: str):
    self.logs = []  # ⚠️ No type hint
    self.state = {}  # ⚠️ No type hint
```

**Fix**:
```python
from typing import List, Dict, Any

def __init__(self, name: str) -> None:
    self.logs: List[Dict[str, str]] = []
    self.state: Dict[str, Any] = {}
```

#### Issue #10: Missing Return Type Annotations
**Location**: Multiple functions

```python
# backend/app/main.py:48
async def get_result(task_id: str):  # ⚠️ No return type
    
# backend/app/main.py:42  
async def get_logs():  # ⚠️ No return type
```

**Fix**:
```python
async def get_result(task_id: str) -> Dict[str, Any]:
    # ...

async def get_logs() -> List[Dict[str, str]]:
    # ...
```

---

### 4. Race Condition Issues 🏁

#### Issue #11: Thread-Unsafe Shared State in Pipeline
**Location**: `backend/app/pipeline.py:17-25`

```python
class DocumentPipeline:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.extractor = ExtractorAgent()
        self.router = RouterAgent()
        self.results = {}  # ⚠️ RACE CONDITION - Not thread-safe!
        self.active_tasks = []  # ⚠️ RACE CONDITION
```

**Problem**:
- Multiple concurrent requests modify shared state
- Dictionary and list operations are not atomic
- Can cause data corruption, lost updates, or crashes

**Example Scenario**:
```
Request A: pipeline.results[task1] = result_a
Request B: pipeline.results[task2] = result_b  
# If these happen simultaneously, one might be lost

Request A: self.active_tasks.append(task1)
Request B: self.active_tasks.remove(task1)
# ValueError: task1 not in list (timing issue)
```

**Fix**:
```python
from threading import Lock
from typing import Dict, List
import threading

class DocumentPipeline:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.extractor = ExtractorAgent()
        self.router = RouterAgent()
        self.results: Dict[str, Any] = {}
        self.active_tasks: List[str] = []
        self._results_lock = Lock()
        self._tasks_lock = Lock()
    
    def process(self, text: str) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        
        with self._tasks_lock:
            self.active_tasks.append(task_id)
        
        try:
            # Processing logic...
            final_result = {
                "task_id": task_id,
                # ...
            }
            
            with self._results_lock:
                self.results[task_id] = final_result
            
            return final_result
        finally:
            with self._tasks_lock:
                if task_id in self.active_tasks:
                    self.active_tasks.remove(task_id)
```

**Better Fix - Use Thread-Safe Collections**:
```python
from collections.abc import MutableMapping
from queue import Queue
import threading

class ThreadSafeDict(MutableMapping):
    def __init__(self):
        self._dict = {}
        self._lock = threading.RLock()
    
    def __getitem__(self, key):
        with self._lock:
            return self._dict[key]
    
    def __setitem__(self, key, value):
        with self._lock:
            self._dict[key] = value
    
    # Implement other required methods...

class DocumentPipeline:
    def __init__(self):
        # Use thread-safe collections
        self.results = ThreadSafeDict()
        self.active_tasks = set()  # Sets are more appropriate here
        self._tasks_lock = threading.RLock()
```

#### Issue #12: Race Condition in Frontend State Updates
**Location**: `frontend/app/page.tsx:38-56`

```typescript
useEffect(() => {
  fetchData()
  // ⚠️ RACE CONDITION - Multiple concurrent fetchData calls
  const interval = setInterval(fetchData, 2000)
  return () => clearInterval(interval)
}, [])
```

**Problem**:
- `fetchData` is called immediately, then every 2 seconds
- If a fetch takes > 2 seconds, multiple fetches overlap
- Race condition: which response updates state first?
- Can cause stale data to overwrite fresh data

**Example Scenario**:
```
T=0s:    Fetch A starts (takes 3s)
T=2s:    Fetch B starts (takes 1s)
T=3s:    Fetch B completes, updates state with data from T=2s
T=3s:    Fetch A completes, updates state with data from T=0s (STALE!)
```

**Fix**:
```typescript
const [isFetching, setIsFetching] = useState(false)

const fetchData = async () => {
  if (isFetching) return  // Prevent concurrent fetches
  
  setIsFetching(true)
  try {
    const statusRes = await fetch(`${API_URL}/status`)
    const statusData = await statusRes.json()
    setStatus(statusData)

    const logsRes = await fetch(`${API_URL}/logs`)
    const logsData = await logsRes.json()
    setLogs(logsData)
  } catch (error) {
    console.error('Fetch error:', error)
  } finally {
    setIsFetching(false)
  }
}

useEffect(() => {
  fetchData()
  const interval = setInterval(fetchData, 2000)
  return () => clearInterval(interval)
}, [])
```

**Better Fix - Use AbortController**:
```typescript
useEffect(() => {
  let abortController: AbortController | null = null
  
  const fetchData = async () => {
    // Cancel previous fetch if still running
    if (abortController) {
      abortController.abort()
    }
    
    abortController = new AbortController()
    
    try {
      const statusRes = await fetch(`${API_URL}/status`, {
        signal: abortController.signal
      })
      const statusData = await statusRes.json()
      setStatus(statusData)

      const logsRes = await fetch(`${API_URL}/logs`, {
        signal: abortController.signal
      })
      const logsData = await logsRes.json()
      setLogs(logsData)
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Fetch error:', error)
      }
    }
  }
  
  fetchData()
  const interval = setInterval(fetchData, 2000)
  
  return () => {
    clearInterval(interval)
    if (abortController) {
      abortController.abort()
    }
  }
}, [])
```

#### Issue #13: Race Condition in File Upload
**Location**: `frontend/app/page.tsx:49-56`

```typescript
const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  // ...
  const result = await response.json()
  
  // ⚠️ RACE CONDITION - Reading from stale closure
  setResults([result, ...results])  // Uses old 'results' value!
  // ...
}
```

**Problem**:
- `results` is captured in closure when function is created
- If user uploads multiple files quickly, updates can be lost
- Each upload sees the same old `results` value

**Example**:
```
Initial: results = []
Upload A starts: captures results = []
Upload B starts: captures results = []
Upload A completes: sets results = [A]
Upload B completes: sets results = [B]  // Lost A!
```

**Fix**:
```typescript
const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0]
  if (!file) return

  setIsProcessing(true)

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/process`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) throw new Error('Upload failed')
    
    const result = await response.json()
    
    // Use functional update to avoid stale closure
    setResults(prev => [result, ...prev])
    
    await fetchData()
  } catch (error) {
    console.error('Upload error:', error)
  } finally {
    setIsProcessing(false)
  }
}
```

---

## Additional Issues to Consider

### Code Quality Issues
1. **Magic Numbers**: Hardcoded confidence thresholds in classifier
2. **No Logging**: Missing proper logging in production code
3. **No Validation**: Agent outputs not validated before passing to next agent
4. **No Tests**: No unit tests, integration tests, or E2E tests
5. **Tight Coupling**: Pipeline directly instantiates agents (should use dependency injection)

### Performance Issues
1. **Inefficient Polling**: Frontend polls every 2 seconds (use WebSockets instead)
2. **No Caching**: Repeated fetches for the same data
3. **No Pagination**: Logs and results could grow unbounded
4. **Synchronous Processing**: Pipeline processes documents synchronously (use task queue)

### Maintainability Issues
1. **No Documentation**: Missing docstrings for public APIs
2. **Inconsistent Style**: Mixed naming conventions
3. **No Configuration**: Hardcoded values (API URLs, timeouts, etc.)
4. **No Monitoring**: No metrics, alerts, or observability

---

## Review Checklist

Use this checklist when reviewing the code:

### Security Review
- [ ] Check for SQL injection vulnerabilities
- [ ] Verify input validation on all endpoints
- [ ] Review CORS configuration
- [ ] Check for XSS vulnerabilities
- [ ] Verify authentication/authorization (if required)
- [ ] Check for sensitive data exposure
- [ ] Review regex patterns for ReDoS
- [ ] Check file upload restrictions

### Error Handling Review
- [ ] Every async function has try-catch
- [ ] Errors are logged appropriately
- [ ] Users receive helpful error messages
- [ ] No silent failures
- [ ] Proper HTTP status codes used
- [ ] Graceful degradation implemented

### Type Safety Review
- [ ] No use of `any` or `Any` types
- [ ] All function parameters typed
- [ ] All function return types specified
- [ ] Proper interfaces/models defined
- [ ] Type guards used where needed
- [ ] Generic types used appropriately

### Concurrency Review
- [ ] Shared state is protected with locks
- [ ] No race conditions in state updates
- [ ] Proper use of async/await
- [ ] AbortController for fetch requests
- [ ] Functional state updates in React
- [ ] Thread-safe collections used

### General Code Quality
- [ ] Functions are small and focused
- [ ] Clear naming conventions
- [ ] Appropriate comments
- [ ] No code duplication
- [ ] Separation of concerns
- [ ] Proper error messages
- [ ] Configuration externalized
- [ ] Tests exist and pass

---

## Testing the Issues

### Security Testing

**Test CORS Issue**:
```bash
# From a different origin
curl -X POST http://localhost:8000/process \
  -H "Origin: http://malicious-site.com" \
  -F "file=@test.txt" \
  -v
# Should be rejected but isn't!
```

**Test File Size Limit**:
```bash
# Create large file
dd if=/dev/zero of=large.txt bs=1M count=100

# Try to upload
curl -X POST http://localhost:8000/process \
  -F "file=@large.txt"
# Should be rejected but isn't!
```

### Race Condition Testing

**Test Backend Race Condition**:
```python
import asyncio
import aiohttp

async def upload_many():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.post(
                'http://localhost:8000/process',
                data={'file': open('test.txt', 'rb')}
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Check status - active_tasks should be 0
        status = await session.get('http://localhost:8000/status')
        print(await status.json())
        # Often shows wrong count due to race condition!

asyncio.run(upload_many())
```

**Test Frontend Race Condition**:
```javascript
// In browser console
// Upload files rapidly
for (let i = 0; i < 5; i++) {
  // Simulate rapid uploads
  setTimeout(() => {
    document.querySelector('input[type="file"]').click()
  }, i * 100)
}
// Check if all results appear or some are lost
```

---

## Summary

This code review exercise contains:

**Security**: 4 issues
- CORS configuration
- Input validation
- SQL injection risk
- ReDoS vulnerability

**Error Handling**: 3 issues
- No try-catch blocks
- Silent failures
- Unhandled promises

**Type Safety**: 3 issues
- Overuse of Any
- Missing type annotations
- Missing return types

**Race Conditions**: 3 issues
- Thread-unsafe dict/list
- Concurrent fetch calls
- Stale closure in uploads

**Total**: 13 major issues + additional code quality concerns

Good luck with your review! 🎯
