# RAG System Frontend

React-based user interface for the RAG (Retrieval-Augmented Generation) system.

## Features

- **Chat Interface**: Real-time conversation with the AI agent
- **Document Upload**: Support for PDF, TXT, and Markdown files
- **Document Management**: View, manage, and delete indexed documents
- **Source Citations**: See which documents provided the answer
- **Session Management**: Maintain conversation history per session
- **Responsive Design**: Works on desktop and mobile

## Installation

```bash
npm install
```

## Development

```bash
npm start
```

Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

## Building

```bash
npm run build
```

Builds the app for production to the `build` folder.

## Architecture

- **src/components/ChatWindow.js** - Chat interface for sending messages
- **src/components/DocumentManager.js** - Document upload and management
- **src/api/client.js** - API client for backend communication
- **src/App.js** - Main application container

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000/api`.

### Endpoints Used

- `POST /api/chat` - Send chat message
- `GET /api/chat/history/{session_id}` - Get conversation history
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{doc_id}` - Delete document
- `POST /api/documents/clear` - Clear all documents

## Configuration

The API URL can be configured via `REACT_APP_API_URL` environment variable:

```bash
REACT_APP_API_URL=http://localhost:8000/api npm start
```

Default: `http://localhost:8000/api`
