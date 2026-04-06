const API_BASE_URL = 'http://localhost:8000';

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

  searchPapersWithProgress(query, nResults = 10, useRerank = true, topK = null, onProgress = null) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      let buffer = '';
      let isCompleted = false;

      const cleanup = () => {
        if (isCompleted) return;
        isCompleted = true;
      };

      const processLine = (line) => {
        if (!line.startsWith('data: ')) return;

        try {
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) return;

          const data = JSON.parse(jsonStr);

          if (data.event === 'error') {
            cleanup();
            reject(new Error(data.error || '检索失败'));
            return;
          }

          if (data.event === 'search_complete') {
            cleanup();
            resolve({
              success: true,
              query: data.query,
              total_results: data.total_results,
              results: data.results || [],
            });
            return;
          }

          if (onProgress && typeof onProgress === 'function') {
            onProgress({ type: 'progress', data });
          }
        } catch (e) {
          if (isDevelopment) {
            console.warn('[SSE] Parse warning (may be incomplete):', e.message);
          }
        }
      };

      xhr.open('POST', `${API_BASE_URL}/api/search/stream`, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.responseType = 'text';

      xhr.onprogress = (event) => {
        if (isCompleted) return;

        const newText = event.target.responseText;
        if (!newText) return;

        buffer = newText;

        const lines = buffer.split('\n');
        const completeLines = lines.slice(0, -1);

        for (const line of completeLines) {
          if (line.trim()) {
            processLine(line.trim());
          }
          if (isCompleted) break;
        }
      };

      xhr.onload = () => {
        if (isCompleted) return;

        if (xhr.status >= 200 && xhr.status < 300) {
          const remainingText = buffer;
          if (remainingText.trim()) {
            const lines = remainingText.split('\n');
            for (const line of lines) {
              if (line.trim()) {
                processLine(line.trim());
              }
              if (isCompleted) break;
            }
          }

          if (!isCompleted) {
            cleanup();
            reject(new Error('检索完成但未收到结果'));
          }
        } else {
          cleanup();
          reject(new Error(`请求失败: ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        cleanup();
        reject(new Error('网络连接失败'));
      };

      xhr.onabort = () => {
        cleanup();
        reject(new Error('请求已取消'));
      };

      xhr.send(JSON.stringify({
        query,
        n_results: nResults,
        use_rerank: useRerank,
        top_k: topK,
      }));
    });
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

  generateSurveyWithProgress(topic, nResults = 15, onProgress = null) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      let buffer = '';
      let isCompleted = false;

      const cleanup = () => {
        if (isCompleted) return;
        isCompleted = true;
      };

      const processLine = (line) => {
        if (!line.startsWith('data: ')) return;

        try {
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) return;

          const data = JSON.parse(jsonStr);

          if (data.event === 'report_error') {
            cleanup();
            reject(new Error(data.data?.error || '报告生成失败'));
            return;
          }

          if (data.event === 'report_complete') {
            cleanup();
            resolve({
              success: true,
              report_content: data.data?.report_content || '',
              paper_info: data.data?.paper_info || {},
              citation_stats: data.data?.citation_stats || {},
              generated_at: data.data?.generated_at,
            });
            return;
          }

          if (onProgress && typeof onProgress === 'function') {
            onProgress({
              type: 'progress',
              event: data.event,
              stage: data.data?.stage,
              content: data.data?.content,
              fullContent: data.data?.full_content,
              message: data.data?.message,
              totalPapers: data.data?.total_papers,
            });
          }
        } catch (e) {
          if (isDevelopment) {
            console.warn('[SSE] Parse warning (may be incomplete):', e.message);
          }
        }
      };

      xhr.open('POST', `${API_BASE_URL}/api/report/stream`, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.responseType = 'text';

      xhr.onprogress = (event) => {
        if (isCompleted) return;

        const newText = event.target.responseText;
        if (!newText) return;

        buffer = newText;

        const lines = buffer.split('\n');
        const completeLines = lines.slice(0, -1);

        for (const line of completeLines) {
          if (line.trim()) {
            processLine(line.trim());
          }
          if (isCompleted) break;
        }
      };

      xhr.onload = () => {
        if (isCompleted) return;

        if (xhr.status >= 200 && xhr.status < 300) {
          const remainingText = buffer;
          if (remainingText.trim()) {
            const lines = remainingText.split('\n');
            for (const line of lines) {
              if (line.trim()) {
                processLine(line.trim());
              }
              if (isCompleted) break;
            }
          }

          if (!isCompleted) {
            cleanup();
            reject(new Error('报告生成完成但未收到最终结果'));
          }
        } else {
          cleanup();
          reject(new Error(`请求失败: ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        cleanup();
        reject(new Error('网络连接失败'));
      };

      xhr.onabort = () => {
        cleanup();
        reject(new Error('请求已取消'));
      };

      xhr.send(JSON.stringify({ topic, n_results: nResults }));
    });
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
