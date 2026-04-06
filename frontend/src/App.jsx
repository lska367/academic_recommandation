
import { useState, useRef, useEffect, useCallback } from 'react';
import { BookOpen, AlertCircle, Sparkles, Search } from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { ProgressIndicator } from './components/ProgressIndicator';
import { apiClient } from './api/client';

const MODE_CONFIG = {
  search: { icon: Search, label: '论文检索', placeholder: '输入研究主题，如：深度学习在计算机视觉中的应用' },
  survey: { icon: Sparkles, label: '学术综述', placeholder: '输入主题生成学术综述，如：自然语言处理的最新进展' },
};

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('search');
  const [backendHealth, setBackendHealth] = useState(true);
  const [progressStage, setProgressStage] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiClient.checkHealth();
      setBackendHealth(healthy);
    };
    checkHealth();
  }, []);

  const handleSend = useCallback(async (query, currentMode) => {
    console.log('[App] handleSend called:', { query, currentMode });
    setError(null);
    setProgressStage(null);
    setProgressMessage('');
    setStreamingContent('');
    setIsStreaming(false);

    const userMessage = { role: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (currentMode === 'search') {
        console.log('[App] Calling searchPapersWithProgress...');
        setProgressStage('search_start');
        setProgressMessage('开始检索相关论文...');

        const response = await apiClient.searchPapersWithProgress(
          query,
          10,
          true,
          10,
          (progressData) => {
            console.log('[App] Search progress:', progressData);
            if (progressData.data) {
              setProgressStage(progressData.data.stage);
              setProgressMessage(progressData.data.message);
            }
          }
        );

        console.log('[App] Search response received:', response);

        setProgressStage(null);
        setProgressMessage('');

        if (response.success) {
          const uniquePapers = [];
          const seenPaperIds = new Set();
          for (const result of response.results || []) {
            const paperId = result.metadata?.paper_id;
            if (!seenPaperIds.has(paperId)) {
              seenPaperIds.add(paperId);
              uniquePapers.push(result);
            }
          }

          console.log('[App] Unique papers:', uniquePapers.length);

          const assistantMessage = {
            role: 'assistant',
            content: `找到 ${uniquePapers.length} 篇相关论文：`,
            papers: uniquePapers,
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          throw new Error(response.error || '检索失败');
        }
      } else {
        console.log('[App] Calling generateSurveyWithProgress...');

        setProgressStage('report_start');
        setProgressMessage('正在检索相关论文并生成综述...');

        const assistantMessageId = Date.now();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          isStreaming: true,
          streamingContent: '',
          messageId: assistantMessageId,
        }]);

        setIsStreaming(true);
        setIsLoading(false);

        try {
          const response = await apiClient.generateSurveyWithProgress(
            query,
            15,
            (progressData) => {
              console.log('[App] Survey progress:', progressData);

              if (progressData.stage === 'report_start' || progressData.stage === 'report_content_start') {
                setProgressStage(progressData.stage);
                setProgressMessage(progressData.message || '正在生成报告...');
              }

              if (progressData.event === 'report_chunk' && progressData.fullContent) {
                setMessages(prev => prev.map(msg => {
                  if (msg.messageId === assistantMessageId) {
                    return {
                      ...msg,
                      streamingContent: progressData.fullContent,
                    };
                  }
                  return msg;
                }));
              }
            }
          );

          console.log('[App] Survey response received:', response);

          if (response.success) {
            setMessages(prev => prev.map(msg => {
              if (msg.messageId === assistantMessageId) {
                return {
                  ...msg,
                  content: response.report_content,
                  papers: response.paper_info?.papers || [],
                  isStreaming: false,
                  streamingContent: null,
                };
              }
              return msg;
            }));
          } else {
            throw new Error(response.error || '生成综述失败');
          }
        } catch (err) {
          setMessages(prev => prev.filter(msg => msg.messageId !== assistantMessageId));
          throw err;
        } finally {
          setProgressStage(null);
          setProgressMessage('');
          setIsStreaming(false);
          setStreamingContent('');
        }
      }
    } catch (err) {
      console.error('[App] Error in handleSend:', err);
      const errorMsg = err instanceof Error ? `${err.name}: ${err.message}` : String(err);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
      setProgressStage(null);
      setProgressMessage('');
      setIsStreaming(false);
    }
  }, []);

  const handleQuickSearch = useCallback((query, targetMode) => {
    setMode(targetMode);
    handleSend(query, targetMode);
  }, [handleSend]);

  const currentModeConfig = MODE_CONFIG[mode];

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-indigo-50 dark:from-slate-950 dark:via-purple-950/20 dark:to-indigo-950/30">
      <header className="bg-white/70 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/30">
                <BookOpen className="text-white" size={28} />
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-900 shadow-sm" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-slate-900 to-purple-700 dark:from-white dark:to-purple-300 bg-clip-text text-transparent">
                学术推荐系统
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                智能论文检索 · 多模态理解 · 学术综述生成
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {!backendHealth && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-50 dark:bg-red-950/50 rounded-lg border border-red-200 dark:border-red-900/50">
                <AlertCircle size={14} className="text-red-600 dark:text-red-400" />
                <span className="text-xs font-medium text-red-700 dark:text-red-300">
                  后端连接失败
                </span>
              </div>
            )}
            
            <div className="flex bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700/50">
              {Object.entries(MODE_CONFIG).map(([key, config]) => {
                const Icon = config.icon;
                const isActive = mode === key;
                return (
                  <button
                    key={key}
                    onClick={() => setMode(key)}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                      ${isActive 
                        ? 'bg-white dark:bg-slate-700 text-purple-700 dark:text-purple-200 shadow-sm ring-1 ring-purple-200/50 dark:ring-purple-500/30' 
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/50 dark:hover:bg-slate-700/50'}
                    `}
                  >
                    <Icon size={16} />
                    {config.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto scroll-smooth">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-160px)]">
              <div className="relative mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/40 dark:to-indigo-900/40 rounded-[32px] flex items-center justify-center shadow-2xl shadow-purple-500/10">
                  <BookOpen size={64} className="text-purple-600 dark:text-purple-400" />
                </div>
                <div className="absolute -top-3 -right-3 w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg shadow-amber-500/30">
                  <Sparkles size={20} className="text-white" />
                </div>
              </div>
              
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3 text-center">
                欢迎使用学术推荐系统
              </h2>
              <p className="text-slate-600 dark:text-slate-400 max-w-xl text-center mb-10 leading-relaxed">
                输入您感兴趣的研究主题，系统将利用多模态检索技术帮您找到相关论文或生成全面的学术综述报告
              </p>
              
              <div className="grid gap-4 w-full max-w-2xl">
                <button
                  onClick={() => handleQuickSearch('深度学习在计算机视觉中的应用', 'search')}
                  className="group text-left p-5 bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl hover:border-purple-300 dark:hover:border-purple-700/50 hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-300"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Search size={20} className="text-white" />
                    </div>
                    <div>
                      <span className="font-semibold text-slate-900 dark:text-white block mb-1">
                        🔍 论文检索示例
                      </span>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        深度学习在计算机视觉中的应用
                      </p>
                    </div>
                  </div>
                </button>
                
                <button
                  onClick={() => handleQuickSearch('自然语言处理的最新进展', 'survey')}
                  className="group text-left p-5 bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl hover:border-purple-300 dark:hover:border-purple-700/50 hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-300"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Sparkles size={20} className="text-white" />
                    </div>
                    <div>
                      <span className="font-semibold text-slate-900 dark:text-white block mb-1">
                        ✨ 学术综述示例
                      </span>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        自然语言处理的最新进展
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6 mb-8">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  papers={message.papers}
                  isLoading={false}
                  isStreaming={message.isStreaming}
                  streamingContent={message.streamingContent}
                />
              ))}
              {progressStage && (
                <div className="max-w-3xl mx-auto">
                  <ProgressIndicator
                    stage={progressStage}
                    message={progressMessage}
                  />
                </div>
              )}
              {isLoading && !progressStage && (
                <ChatMessage role="assistant" isLoading={true} />
              )}
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}

          {error && (
            <div className="fixed bottom-32 left-1/2 -translate-x-1/2 z-50 max-w-lg w-full px-4">
              <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-950/60 dark:to-rose-950/60 border border-red-200 dark:border-red-800/50 rounded-2xl shadow-2xl backdrop-blur-sm">
                <div className="flex items-start gap-3">
                  <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" size={20} />
                  <div className="flex-1">
                    <p className="text-red-900 dark:text-red-100 font-semibold text-sm">
                      发生错误
                    </p>
                    <p className="text-red-700 dark:text-red-300 text-sm mt-1 leading-relaxed whitespace-pre-wrap">
                      {error}
                    </p>
                    <p className="text-red-600 dark:text-red-400 text-xs mt-2">
                      (请打开浏览器控制台查看详细调试信息)
                    </p>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 p-1 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
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
        placeholder={currentModeConfig.placeholder}
      />
    </div>
  );
}

export default App;
