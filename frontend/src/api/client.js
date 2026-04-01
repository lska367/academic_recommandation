
const API_BASE_URL = 'http://localhost:8000';

// 检测是否为开发环境
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export const apiClient = {
  async searchPapers(query, nResults = 10, useRerank = false) {
    try {
      if (isDevelopment) {
        console.log('[API] Searching papers:', { query, nResults, useRerank });
      }
      
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          n_results: nResults,
          use_rerank: useRerank,
        }),
      });

      if (isDevelopment) {
        console.log('[API] Search response status:', response.status, response.statusText);
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        if (isDevelopment) {
          console.error('[API] Search error response:', errorText);
        }
        throw new Error(`搜索失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (isDevelopment) {
        console.log('[API] Search success:', data);
      }
      return data;
    } catch (error) {
      if (isDevelopment) {
        console.error('[API] Search error:', error);
      }
      throw error;
    }
  },

  async generateSurvey(topic, nResults = 15) {
    try {
      if (isDevelopment) {
        console.log('[API] Generating survey:', topic);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          n_results: nResults,
        }),
      });

      if (isDevelopment) {
        console.log('[API] Report response status:', response.status, response.statusText);
      }

      if (!response.ok) {
        const errorText = await response.text();
        if (isDevelopment) {
          console.error('[API] Report error response:', errorText);
        }
        throw new Error(`生成综述失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (isDevelopment) {
        console.log('[API] Report success:', data);
      }
      return data;
    } catch (error) {
      if (isDevelopment) {
        console.error('[API] Report error:', error);
      }
      throw error;
    }
  },

  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (isDevelopment) {
        console.log('[API] Health check:', response.ok);
      }
      return response.ok;
    } catch (error) {
      if (isDevelopment) {
        console.error('[API] Health check error:', error);
      }
      return false;
    }
  },
};
