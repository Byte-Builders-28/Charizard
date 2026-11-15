/**
 * Centralized API Client for CHARIZARD
 * Conforms to Section 6 of AGENTS.md
 */

const API_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.PUBLIC_API_BASE_URL)
  ? import.meta.env.PUBLIC_API_BASE_URL
  : 'http://127.0.0.1:8000';

/**
 * Shared internal request helper
 * Handles serialization, response parsing, and standard HTTP errors
 */
async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers
    });
  } catch (networkError) {
    throw new Error(`Network failure connecting to API at ${url}: ${networkError.message}`);
  }

  let data;
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    try {
      data = await response.json();
    } catch (parseError) {
      throw new Error(`Failed to parse JSON response from ${path}: ${parseError.message}`);
    }
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const detail = (data && typeof data === 'object' && data.detail) ? data.detail : response.statusText;
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

/**
 * Health check
 * GET /health
 */
export async function getHealth() {
  return request('/health');
}

/**
 * Investigation listing
 * GET /investigations
 */
export async function getInvestigations(params = {}) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return request(`/investigations${queryString ? `?${queryString}` : ''}`);
}

/**
 * Investigation details
 * GET /investigations/{id}
 */
export async function getInvestigation(id) {
  if (!id) {
    throw new Error('Investigation ID is required');
  }
  return request(`/investigations/${encodeURIComponent(id)}`);
}

/**
 * Telemetry
 * GET /investigations/{id}/telemetry
 */
export async function getInvestigationTelemetry(id, limit) {
  if (!id) {
    throw new Error('Investigation ID is required');
  }
  const query = new URLSearchParams();
  if (limit !== undefined && limit !== null) {
    query.set('limit', String(limit));
  }
  const queryString = query.toString();
  return request(`/investigations/${encodeURIComponent(id)}/telemetry${queryString ? `?${queryString}` : ''}`);
}

/**
 * Search
 * GET /search
 */
export async function searchInvestigations(params = {}) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return request(`/search${queryString ? `?${queryString}` : ''}`);
}

/**
 * Comparison
 * POST /compare
 * @param {string[]} ids - Array of 2 to 3 investigation IDs
 */
export async function compareInvestigations(ids) {
  if (!Array.isArray(ids) || ids.length < 2 || ids.length > 3) {
    throw new Error('Comparison requires an array of 2 to 3 investigation IDs');
  }
  // API expects a plain JSON array, not a wrapped object
  return request('/compare', {
    method: 'POST',
    body: ids
  });
}

/**
 * Research agent
 * POST /chat?user={user}
 * @param {string} message - Message text
 * @param {string} user - User/session identifier (1 to 100 characters)
 */
export async function sendAgentMessage(message, user = 'researcher-session-default') {
  if (!message || typeof message !== 'string') {
    throw new Error('Message is required and must be a string');
  }
  const query = new URLSearchParams({ user: String(user) });
  return request(`/chat?${query.toString()}`, {
    method: 'POST',
    body: { msg: message }
  });
}
