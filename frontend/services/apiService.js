// ===========================
// API Configuration
// ===========================
const API_CONFIG = {
  baseURL: "https://8080-kode-ws-4c2092c45.hebbale.academy", // Configure the relevant backend url
  headers: {
  "Content-Type": "application/json",
  },
};

// ===========================
// Helper Functions
// ===========================

// Build full URL
const buildURL = (endpoint) => `${API_CONFIG.baseURL}${endpoint}`;

// Handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `HTTP error ${response.status}`);
  }
  return response.json();
};

// ===========================
// API Service Class
// ===========================
class ApiService {
  // ---------- GET ----------
  static async get(endpoint, params = {}) {
    try {
      const query = new URLSearchParams(params).toString();
      const url = `${buildURL(endpoint)}${query ? `?${query}` : ""}`;
      const response = await fetch(url, {
        method: "GET",
        headers: API_CONFIG.headers,
      });
      return await handleResponse(response);
    } catch (error) {
      console.error("GET Request Error:", error);
      throw error;
    }
  }

  // ---------- POST ----------
  static async post(endpoint, data = {}) {
    try {
      const response = await fetch(buildURL(endpoint), {
        method: "POST",
        headers: API_CONFIG.headers,
        body: JSON.stringify(data),
      });
      return await handleResponse(response);
    } catch (error) {
      console.error("POST Request Error:", error);
      throw error;
    }
  }

  // ---------- PUT ----------
  static async put(endpoint, data = {}) {
    try {
      const response = await fetch(buildURL(endpoint), {
        method: "PUT",
        headers: API_CONFIG.headers,
        body: JSON.stringify(data),
      });
      return await handleResponse(response);
    } catch (error) {
      console.error("PUT Request Error:", error);
      throw error;
    }
  }

  // ---------- DELETE ----------
  static async delete(endpoint) {
    try {
      const response = await fetch(buildURL(endpoint), {
        method: "DELETE",
        headers: API_CONFIG.headers,
      });
      return await handleResponse(response);
    } catch (error) {
      console.error("DELETE Request Error:", error);
      throw error;
    }
  }

  // ---------- HEADER MANAGEMENT ----------
  static setHeader(key, value) {
    API_CONFIG.headers[key] = value;
  }

  // ---------- POST WITH STREAM ----------
  // Supports streaming responses (SSE-like or newline-delimited)
  // onChunk: callback for each parsed chunk
  static async postWithStream(endpoint, data = {}, onChunk = null, options = {}) {
    try {
      const streamHeaders = {
        ...API_CONFIG.headers,
        Accept: "text/event-stream, application/json",
        ...options.headers,
      };

      const response = await fetch(buildURL(endpoint), {
        method: "POST",
        headers: streamHeaders,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errBody = await response.text().catch(() => null);
        throw new Error(`HTTP error! status: ${response.status} body: ${errBody}`);
      }

      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (buffer.trim() && onChunk) {
            try {
              const parsed = tryParseChunk(buffer);
              if (parsed !== null) await onChunk(parsed);
            } catch (e) {
              console.warn("Error parsing final chunk:", e);
            }
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Handle newline or "data:" (SSE format)
        let newlineIndex;
        while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
          const line = buffer.slice(0, newlineIndex).trim();
          buffer = buffer.slice(newlineIndex + 1);
          if (!line) continue;

          const processed = line.startsWith("data:")
            ? line.replace(/^data:\s*/, "")
            : line;

          if (onChunk) {
            try {
              const parsed = tryParseChunk(processed);
              if (parsed !== null) await onChunk(parsed);
            } catch (e) {
              console.warn("Error parsing chunk:", e);
            }
          }
        }
      }

      return { success: true };
    } catch (error) {
      console.error("Streaming POST Request Error:", error);
      throw error;
    }
  }
}

// ===========================
// Helper: Safe JSON parser
// ===========================
function tryParseChunk(str) {
  try {
    return JSON.parse(str);
  } catch {
    return str;
  }
}

// ===========================
// Exports
// ===========================
export { buildURL, API_CONFIG };
export default ApiService;
