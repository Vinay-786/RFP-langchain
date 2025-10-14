# RFP API Documentation

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
  "stage": "Completed"
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
  "stage": "Completed"
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


