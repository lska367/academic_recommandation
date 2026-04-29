const API_BASE_URL = 'http://localhost:8000';

export const apiClient = {
  // ========== 认证相关 ==========

  async verifyEmail(email) {
    const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    return response.json();
  },

  // ========== 聊天核心 ==========

  sendChatMessage(message, userId, conversationId, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      let buffer = '';
      let isCompleted = false;

      const cleanup = () => { if (isCompleted) return; isCompleted = true; };

      const processLine = (line) => {
        if (!line.startsWith('data: ')) return;
        try {
          const data = JSON.parse(line.slice(6).trim());
          
          if (data.event === 'chat_complete') {
            cleanup();
            resolve(data.data);
            return;
          }
          if (data.event === 'error') {
            cleanup();
            reject(new Error(data.error));
            return;
          }
          if (onProgress) onProgress(data);
        } catch (e) { /* ignore parse errors */ }
      };

      xhr.open('POST', `${API_BASE_URL}/api/chat/stream`, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.responseType = 'text';

      xhr.onprogress = (event) => {
        if (isCompleted) return;
        buffer = event.target.responseText || '';
        const lines = buffer.split('\n');
        for (const line of lines.slice(0, -1)) {
          if (line.trim()) processLine(line.trim());
          if (isCompleted) break;
        }
      };

      xhr.onload = () => {
        if (isCompleted) return;
        const remainingText = buffer || '';
        if (remainingText.trim()) {
          remainingText.split('\n').forEach(line => {
            if (line.trim()) processLine(line.trim());
            if (isCompleted) return;
          });
        }
        if (!isCompleted) cleanup(), reject(new Error('响应不完整'));
      };

      xhr.onerror = () => cleanup(), reject(new Error('网络错误'));
      xhr.onabort = () => cleanup(), reject(new Error('请求已取消'));

      xhr.send(JSON.stringify({
        message,
        user_id: userId,
        conversation_id: conversationId
      }));
    });
  },

  // ========== 用户管理 ==========

  async getUserProfile(userId) {
    const response = await fetch(`${API_BASE_URL}/api/user/profile/${userId}`);
    return response.json();
  },

  async getConversations(userId, limit = 20) {
    const response = await fetch(`${API_BASE_URL}/api/user/conversations/${userId}?limit=${limit}`);
    return response.json();
  },

  async updatePreferences(userId, preferences) {
    const response = await fetch(`${API_BASE_URL}/api/user/preferences/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferences }),
    });
    return response.json();
  },

  // ========== 推荐系统 ==========

  async getPersonalizedRecommendations(userId) {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/personalized/${userId}`, {
      method: 'POST',
    });
    return response.json();
  },

  // ========== 邮件服务 ==========

  async getEmailStatus() {
    const response = await fetch(`${API_BASE_URL}/api/email/status`);
    return response.json();
  },

  async testEmail() {
    const response = await fetch(`${API_BASE_URL}/api/email/test`, { method: 'POST' });
    return response.json();
  },

  async sendTestEmail(userId) {
    const response = await fetch(`${API_BASE_URL}/api/email/send-test/${userId}`, { method: 'POST' });
    return response.json();
  },

  // ========== 调度器控制 ==========

  async getSchedulerStatus() {
    const response = await fetch(`${API_BASE_URL}/api/scheduler/status`);
    return response.json();
  },

  async startScheduler() {
    const response = await fetch(`${API_BASE_URL}/api/scheduler/start`, { method: 'POST' });
    return response.json();
  },

  async stopScheduler() {
    const response = await fetch(`${API_BASE_URL}/api/scheduler/stop`, { method: 'POST' });
    return response.json();
  },

  async runPapersNow() {
    const response = await fetch(`${API_BASE_URL}/api/scheduler/run-papers-now`, { method: 'POST' });
    return response.json();
  },

  async runSurveyNow() {
    const response = await fetch(`${API_BASE_URL}/api/scheduler/run-survey-now`, { method: 'POST' });
    return response.json();
  },

  // ========== 系统信息 ==========

  async getSystemStats() {
    const response = await fetch(`${API_BASE_URL}/api/system/stats`);
    return response.json();
  },
};
