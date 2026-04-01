import { useState, useRef, useEffect } from 'react';
import { BookOpen, AlertCircle, RefreshCw } from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { apiClient } from './api/client';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('search');
  const [backendHealth, setBackendHealth] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiClient.checkHealth();
      setBackendHealth(healthy);
    };
    checkHealth();
  }, []);

  const handleSend = async (query, currentMode) => {
    setError(null);
    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (currentMode === 'search') {
        const response = await apiClient.searchPapers(query);
        const assistantMessage = {
          role: 'assistant',
          content: `找到 ${response.total_results} 篇相关论文：`,
          papers: response.results,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const response = await apiClient.generateSurvey(query);
        if (response.success) {
          const assistantMessage = {
            role: 'assistant',
            content: response.report_content,
            papers: response.paper_info?.papers || [],
          };
          setMessages((prev) => [...prev, assistantMessage]);
        } else {
          throw new Error(response.error || '生成综述失败');
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center">
              <BookOpen className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                学术推荐系统
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                智能论文检索与学术综述生成
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!backendHealth && (
              <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle size={16} />
                <span>后端连接失败</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-20 text-center">
              <div className="w-24 h-24 bg-purple-100 dark:bg-purple-900/30 rounded-3xl flex items-center justify-center mb-6">
                <BookOpen size={48} className="text-purple-600 dark:text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                欢迎使用学术推荐系统
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mb-8">
                输入您感兴趣的研究主题，系统将帮您检索相关论文或生成学术综述报告
              </p>
              <div className="grid gap-4 w-full max-w-lg">
                <button
                  onClick={() => handleSend('深度学习在计算机视觉中的应用', 'search')}
                  className="text-left p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-500 hover:shadow-sm transition-all"
                >
                  <span className="font-medium text-gray-900 dark:text-white">
                    🔍 检索论文
                  </span>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    深度学习在计算机视觉中的应用
                  </p>
                </button>
                <button
                  onClick={() => handleSend('自然语言处理的最新进展', 'survey')}
                  className="text-left p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-500 hover:shadow-sm transition-all"
                >
                  <span className="font-medium text-gray-900 dark:text-white">
                    ✨ 生成综述
                  </span>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    自然语言处理的最新进展
                  </p>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-1">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  papers={message.papers}
                />
              ))}
              {isLoading && (
                <ChatMessage role="assistant" isLoading={true} />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <div className="flex items-center gap-3">
                <AlertCircle className="text-red-600 dark:text-red-400" size={20} />
                <div className="flex-1">
                  <p className="text-red-800 dark:text-red-200 font-medium">
                    发生错误
                  </p>
                  <p className="text-red-600 dark:text-red-400 text-sm mt-1">
                    {error}
                  </p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                >
                  <RefreshCw size={20} />
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <ChatInput
        onSend={handleSend}
        isLoading={isLoading}
        mode={mode}
        onModeChange={setMode}
      />
    </div>
  );
}

export default App;
