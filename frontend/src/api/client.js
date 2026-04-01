const API_BASE_URL = 'http://localhost:8000';

export const apiClient = {
  async searchPapers(query, nResults = 10, useRerank = true) {
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

    if (!response.ok) {
      throw new Error('搜索失败');
    }

    return response.json();
  },

  async generateSurvey(topic, nResults = 15) {
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

    if (!response.ok) {
      throw new Error('生成综述失败');
    }

    return response.json();
  },

  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },
};
