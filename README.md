# RFP API Documentation

## Workflow Example

Here is a complete workflow example using `curl` to test the API.

**Prerequisites:**

*   You need an authentication token. Replace `YOUR_TOKEN` with your actual token.
*   You need a project ID, which you get from the project creation step. Replace `PROJECT_ID` accordingly.
*   Have a sample document ready. Replace `/path/to/your/document.docx` with the actual file path.

### 1. Create a Project

```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects/ \
-H "Authorization: Token YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "Project Alpha",
    "description": "Initial test project for RAG.",
    "type": "Technology",
    "stage": "discovery",
    "due_date": "2025-12-31",
    "value": 50000
}'
```

### 2. Upload a Document

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/ \
-H "Authorization: Token YOUR_TOKEN" \
-H "Content-Type: multipart/form-data" \
-F "project=PROJECT_ID" \
-F "document_file=@/path/to/your/document.docx"
```

### 3. Insert Document into RAG

```bash
curl -X POST http://127.0.0.1:8000/api/v1/insert-rag \
-H "Authorization: Token YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "project_id": "PROJECT_ID"
}'
```

### 4. Query the RAG

```bash
curl -X POST http://127.0.0.1:8000/api/v1/query \
-H "Authorization: Token YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "project_id": "PROJECT_ID",
    "prompt": "What is the main topic of the document?"
}'
```

## API Endpoints

### 1. Projects
**View Class:** `ProjectViewSet`

#### List All Projects
- **Endpoint:** `/projects/`
- **Method:** `GET`
- **Request Body:** None
- **Response:** List of project objects

#### Create Project
- **Endpoint:** `/projects/`
- **Method:** `POST`
- **Request Body:**
```json
{
  "name": "Customer Identity Management Solution",
  "type": "Software Implementation",
  "description": "Implementation of CIAM solution",
  "due_date": "09-10-2025 12:31",
  "value": 150000.00,
  "stage": "Completed",
  "manager": "itsvinay.in@gmail.com",
  "primary_contacts_ids": [
            {
                "id": 1,
                "email": "itsvinay.in@gmail.com",
                "first_name": "Vinay",
                "last_name": "Kumar"
            }
        ]
}
```
- **Response:** Created project object

#### Get Project Details
- **Endpoint:** `/projects/{id}/`
- **Method:** `GET`
- **Request Body:** None
- **Response:** Project object

#### Update Project
- **Endpoint:** `/projects/{id}/`
- **Method:** `PUT` or `PATCH`
- **Request Body:** Same as Create (PUT requires all fields, PATCH allows partial)
```json
{
  "name": "Customer Identity Management Solution",
  "type": "Software Implementation",
  "description": "Implementation of CIAM solution",
  "due_date": "09-10-2025 12:31",
  "value": 150000.00,
  "stage": "Completed",
  "manager": "itsvinay.in@gmail.com",
  "primary_contacts_ids": [
            {
                "id": 1,
                "email": "itsvinay.in@gmail.com",
                "first_name": "Vinay",
                "last_name": "Kumar"
            }
        ]
}
```
- **Response:** Updated project object

#### Delete Project
- **Endpoint:** `/projects/{id}/`
- **Method:** `DELETE`
- **Request Body:** None
- **Response:** 204 No Content

---


### 2. Documents
**View Class:** `RFPDocumentViewSet`

#### List All Documents
- **Endpoint:** `/documents/`
- **Method:** `GET`
- **Request Body:** None
- **Response:** List of document objects

#### Upload Document
- **Endpoint:** `/documents/`
- **Method:** `POST`
- **Request Body:** `multipart/form-data`
```
document_file: <file>
uploaded_by: <email_id>
project: <project_id>
```
- **Response:** Created document object with file metadata

#### Get Document Details
- **Endpoint:** `/documents/{id}/`
- **Method:** `GET`
- **Request Body:** None
- **Response:** Document object

#### Update Document
- **Endpoint:** `/documents/{id}/`
- **Method:** `PUT` or `PATCH`
- **Request Body:** `multipart/form-data`
```
document_file: <file> (optional)
uploaded_by: <email_id>
project: <project_id> (optional)
```
- **Response:** Updated document object

#### Delete Document
- **Endpoint:** `/documents/{id}/`
- **Method:** `DELETE`
- **Request Body:** None
- **Response:** 204 No Content

---


### 3. RAG Operations

#### Insert Documents to RAG
**View Class:** `InsertRAGView`
- **Endpoint:** `/insert-rag`
- **Method:** `POST`
- **Request Body:**
```json
{
  "project_id": 1
}
```
- **Response:**
```json
{
  "message": "Successfully inserted 87 chunks for project 1.",
  "project_id": 1,
  "documents_processed": 2
}
```

#### Query RAG System
**View Class:** `QueryRAGView`
- **Endpoint:** `/query`
- **Method:** `POST`
- **Request Body:**
```json
{
  "prompt": "What are the main requirements for the identity management system?",
  "project_id": 1
}
```
- **Response:**
```json
{
  "query": "What are the main requirements for the identity management system?",
  "answer": "Based on the documents, the main requirements include..."
}
```

---


### 4. AI Chat
**View Class:** `OpenAIChat`

#### Chat with GPT
- **Endpoint:** `/chatai`
- **Method:** `POST`
- **Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Help me write an introduction for an RFP response"
    }
  ]
}
```
- **Response:**
```json
{
  "response": "Here's a professional introduction for your RFP response..."
}
```
---


### 5. RFP Generation
**View Class:** `GenerateRFPView`

#### Generate RFP Response Document
- **Endpoint:** `/generate-rfp`
- **Method:** `POST`
- **Request Body:**
```json
{
  "project_id": 1
}
```
- **Response:**
  - Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - Downloads a formatted `.docx` file
  - Automatically saves to server: `media/generated_rfps/YYYY/MM/DD/`
---


