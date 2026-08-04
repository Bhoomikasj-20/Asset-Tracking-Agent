const API_BASE = import.meta.env.VITE_API_URL || '';

async function handleResponse(response: Response) {
  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(errorText || `HTTP error ${response.status}`);
  }
  return response.json();
}

const api = {
  async get<T = unknown>(endpoint: string, params: Record<string, string> = {}): Promise<T> {
    const query = new URLSearchParams(params).toString();
    const url = `${API_BASE}${endpoint}${query ? `?${query}` : ''}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse(response);
  },

  async post<T = unknown>(endpoint: string, data: unknown = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async put<T = unknown>(endpoint: string, data: unknown = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async del<T = unknown>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse(response);
  },

  async postStream(
    endpoint: string,
    data: unknown,
    onChunk: (chunk: unknown) => void
  ): Promise<void> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream, application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errBody = await response.text().catch(() => null);
      throw new Error(`HTTP error! status: ${response.status} body: ${errBody}`);
    }

    if (!response.body) throw new Error('ReadableStream not supported');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        if (buffer.trim()) {
          try {
            const parsed = JSON.parse(buffer);
            onChunk(parsed);
          } catch { /* ignore */ }
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      let newlineIndex: number;
      while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);
        if (!line) continue;

        const processed = line.startsWith('data:') ? line.replace(/^data:\s*/, '') : line;
        try {
          const parsed = JSON.parse(processed);
          onChunk(parsed);
        } catch { /* ignore non-JSON lines */ }
      }
    }
  },
};

export default api;
