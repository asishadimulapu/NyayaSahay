/**
 * API Service Module
 * Handles all communication with the FastAPI backend
 */

// Use environment variable in production, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


/**
 * Get auth headers if user is logged in
 */
function getAuthHeaders() {
    const saved = localStorage.getItem('nyayasahay_user');
    if (saved) {
        const user = JSON.parse(saved);
        if (user.token) {
            return { 'Authorization': `Bearer ${user.token}` };
        }
    }
    return {};
}

/**
 * Send a chat query to the RAG pipeline
 */
export async function sendChatMessage(query, sessionId = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: JSON.stringify({
                query: query,
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            throw new Error('Unable to connect to the server. Please ensure the backend is running.');
        }
        throw error;
    }
}

/**
 * Get user's chat sessions (requires auth)
 */
export async function getChatSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                return []; // Not authenticated, return empty
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to fetch sessions');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Get a specific chat session with messages (requires auth)
 */
export async function getChatSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to fetch session');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Delete a chat session (requires auth)
 */
export async function deleteChatSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to delete session');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Check if the backend is healthy
 */
export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('Backend is not healthy');
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Backend is not reachable');
        }
        throw error;
    }
}

/**
 * Register a new user
 */
export async function registerUser(name, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: name,
                email: email,
                password: password,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Registration failed');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Login user
 */
export async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Invalid credentials');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Upload a file for document analysis
 */
export async function uploadFile(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/v1/upload`, {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
            },
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'File upload failed');
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Unable to connect to server');
        }
        throw error;
    }
}

/**
 * Send a chat query with file context
 */
export async function sendChatWithFile(query, fileContext, sessionId = null) {
    try {
        // Prepend file context to query
        const enhancedQuery = `Based on the following uploaded document content, please answer this question: ${query}\n\n--- UPLOADED DOCUMENT ---\n${fileContext.substring(0, 8000)}\n--- END DOCUMENT ---`;

        const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: JSON.stringify({
                query: enhancedQuery,
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            throw new Error('Unable to connect to the server. Please ensure the backend is running.');
        }
        throw error;
    }
}

export default {
    sendChatMessage,
    checkHealth,
    registerUser,
    loginUser,
    uploadFile,
    sendChatWithFile,
    getChatSessions,
    getChatSession,
    deleteChatSession,
};
