
import { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Mail, Send, Bot, User, BookOpen, Clock, Settings, LogOut, 
  Sparkles, Shield, ChevronRight, Zap, FileText, Bell
} from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { ProgressIndicator } from './components/ProgressIndicator';
import { apiClient } from './api/client';

function App() {
  // 认证状态
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [email, setEmail] = useState('');
  const [userId, setUserId] = useState('');
  const [conversationId, setConversationId] = useState('');
  const [isLoadingAuth, setIsLoadingAuth] = useState(false);
  const [authError, setAuthError] = useState('');

  // 聊天状态
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progressStage, setProgressStage] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  // UI状态
  const [showSettings, setShowSettings] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [emailStatus, setEmailStatus] = useState(null);
  const [schedulerStatus, setSchedulerStatus] = useState(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  useEffect(() => {
    // 检查本地存储的认证信息
    const savedUserId = localStorage.getItem('academic_user_id');
    const savedEmail = localStorage.getItem('academic_user_email');
    
    if (savedUserId && savedEmail) {
      setUserId(savedUserId);
      setEmail(savedEmail);
      setIsAuthenticated(true);
      loadUserProfile(savedUserId);
      loadSchedulerStatus();
    }
  }, []);

  // ========== 认证逻辑 ==========

  const handleEmailVerification = async () => {
    if (!email.trim()) {
      setAuthError('请输入有效的邮箱地址');
      return;
    }

    setIsLoadingAuth(true);
    setAuthError('');

    try {
      const result = await apiClient.verifyEmail(email.trim());
      
      if (result.success) {
        setUserId(result.user_id);
        setConversationId(result.conversation_id);
        setIsAuthenticated(true);

        // 保存到本地存储
        localStorage.setItem('academic_user_id', result.user_id);
        localStorage.setItem('academic_user_email', email.trim());

        console.log('[Auth] ✅ 登录成功:', result.user_id);
        
        // 加载用户数据
        await loadUserProfile(result.user_id);
        await loadSchedulerStatus();
      } else {
        setAuthError(result.error || '验证失败');
      }
    } catch (err) {
      setAuthError('网络错误，请重试');
      console.error('[Auth Error]:', err);
    } finally {
      setIsLoadingAuth(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('academic_user_id');
    localStorage.removeItem('academic_user_email');
    setIsAuthenticated(false);
    setUserId('');
    setEmail('');
    setMessages([]);
    setUserProfile(null);
  };

  // ========== 聊天逻辑 ==========

  const handleSend = async (message) => {
    if (!userId || !isAuthenticated) return;

    console.log('[Chat] Sending message...');
    setError(null);
    setProgressStage(null);
    setProgressMessage('');
    setStreamingContent('');
    setIsStreaming(false);

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try:
      const assistantMsgId = Date.now();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '',
        isStreaming: true,
        streamingContent: '',
        messageId: assistantMsgId,
      }]);

      setIsStreaming(true);
      setIsLoading(false);

      const response = await apiClient.sendChatMessage(
        message,
        userId,
        conversationId,
        (progressData) => {
          console.log('[Chat Progress]:', progressData.event);

          if (progressData.stage) {
            setProgressStage(progressData.stage);
            setProgressMessage(progressData.message || '处理中...');
          }

          if (progressData.event === 'streaming_chunk') {
            setMessages(prev => prev.map(msg => {
              if (msg.messageId === assistantMsgId) {
                return { ...msg, streamingContent: progressData.fullContent };
              }
              return msg;
            }));
          }

          if (progressData.event === 'conversation_complete') {
            if (progressData.data?.conversation_id && !conversationId) {
              setConversationId(progressData.data.conversation_id);
            }
          }
        }
      );

      if (response.success) {
        setMessages(prev => prev.map(msg => {
          if (msg.messageId === assistantMsgId) {
            return {
              ...msg,
              content: response.response,
              papers: response.papers || [],
              isStreaming: false,
              streamingContent: null,
            };
          }
          return msg;
        }));

        // 更新用户画像
        if (response.profile_summary) {
          setUserProfile(prev => ({
            ...prev,
            interests: response.profile_summary.interests || [],
            domains: response.profile_summary.domains || [],
          }));
        }

        // 刷新用户画像
        await loadUserProfile(userId);
      } else {
        throw new Error(response.error || '对话处理失败');
      }

    } catch (err) {
      console.error('[Chat Error]:', err);
      setError(err.message || '发送失败');
      setMessages(prev => prev.filter(msg => msg.messageId !== assistantMsgId));
    } finally {
      setIsLoading(false);
      setProgressStage(null);
      setProgressMessage('');
      setIsStreaming(false);
    }
  };

  // ========== 数据加载方法 ==========

  const loadUserProfile = async (uid) => {
    try {
      const result = await apiClient.getUserProfile(uid);
      if (result.success) {
        setUserProfile(result.profile);
      }
    } catch (e) {
      console.error('Failed to load profile:', e);
    }
  };

  const loadSchedulerStatus = async () => {
    try {
      const result = await apiClient.getSchedulerStatus();
      if (result.success) {
        setSchedulerStatus(result);
      }
    } catch (e) {
      console.error('Failed to load scheduler status:', e);
    }
  };

  // ========== 渲染：邮箱登录页 ==========

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-violet-900 flex items-center justify-center p-6">
        {/* 背景装饰 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000" />
        </div>

        <div className="relative z-10 w-full max-w-md">
          {/* Logo区域 */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/10 backdrop-blur-xl rounded-3xl mb-6 border border-white/20 shadow-2xl">
              <BookOpen size={40} className="text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">
              智能学术助手
            </h1>
            <p className="text-purple-200/80 text-lg font-medium">
              基于AI驱动的个性化学术研究平台
            </p>
          </div>

          {/* 登录卡片 */}
          <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <Mail size={24} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">邮箱验证登录</h2>
                <p className="text-sm text-purple-200/70">请输入您的邮箱以继续</p>
              </div>
            </div>

            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-purple-100 mb-2">电子邮箱地址</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@example.com"
                  onKeyDown={(e) => e.key === 'Enter' && handleEmailVerification()}
                  disabled={isLoadingAuth}
                  className="w-full px-5 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 focus:border-emerald-400/50 transition-all text-base"
                  autoFocus
                />
              </div>

              {authError && (
                <div className="p-3 bg-red-500/20 border border-red-400/30 rounded-xl">
                  <p className="text-red-200 text-sm">{authError}</p>
                </div>
              )}

              <button
                onClick={handleEmailVerification}
                disabled={isLoadingAuth || !email.trim()}
                className="w-full py-4 bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-500 text-white rounded-2xl font-bold text-lg hover:from-emerald-600 hover:via-cyan-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-emerald-500/30 flex items-center justify-center gap-3"
              >
                {isLoadingAuth ? (
                  <>
                    <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    验证中...
                  </>
                ) : (
                  <>
                    <Shield size={20} />
                    验证并进入
                  </>
                )}
              </button>

              <div className="pt-4 border-t border-white/10">
                <p className="text-xs text-purple-300/60 text-center leading-relaxed">
                  🔒 您的邮箱将被安全加密存储<br/>
                  用于接收个性化论文推荐和学术报告推送
                </p>
              </div>
            </div>
          </div>

          {/* 特性说明 */}
          <div className="mt-10 grid grid-cols-3 gap-4">
            {[
              { icon: Bot, title: "AI聊天", desc: "智能学术助手" },
              { icon: FileText, title: "论文推荐", desc: "个性化推送" },
              { icon: Bell, title: "定期报告", desc: "综述自动生成" },
            ].map((feature, idx) => (
              <div key={idx} className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10 text-center">
                <feature.icon size={24} className="mx-auto mb-2 text-purple-300" />
                <h3 className="text-sm font-semibold text-white">{feature.title}</h3>
                <p className="text-xs text-purple-300/60 mt-1">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ========== 渲染：主聊天界面 ==========

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-violet-50/30 to-indigo-50 dark:from-slate-950 dark:via-violet-950/20 dark:to-indigo-950/30">
      
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-900/90 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-11 h-11 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-violet-500/30">
                <Sparkles size={24} className="text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-900" />
            </div>
            
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-violet-700 to-indigo-700 dark:from-violet-300 dark:to-indigo-300 bg-clip-text text-transparent">
                智能学术助手
              </h1>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {email.split('@')[0]}***@{email.split('@')[1]}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* 用户画像标签 */}
            {userProfile?.interests?.length > 0 && (
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-violet-100 dark:bg-violet-950/30 rounded-lg border border-violet-200/50 dark:border-violet-800/40">
                <Zap size={14} className="text-violet-600" />
                <span className="text-xs font-medium text-violet-700 dark:text-violet-300">
                  {userProfile.interests[0]}
                </span>
              </div>
            )}

            <button
              onClick={() => setShowSettings(true)}
              className="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
            >
              <Settings size={20} className="text-slate-600 dark:text-slate-400" />
            </button>

            <button
              onClick={handleLogout}
              className="p-2.5 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-xl transition-colors group"
              title="退出登录"
            >
              <LogOut size={20} className="text-slate-600 dark:text-slate-400 group-hover:text-red-500" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto scroll-smooth">
        <div className="max-w-4xl mx-auto px-6 py-8">
          
          {messages.length === 0 ? (
            /* 欢迎页面 */
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-180px)]">
              
              <div className="relative mb-8">
                <div className="w-36 h-36 bg-gradient-to-br from-violet-100 via-purple-100 to-indigo-100 dark:from-violet-900/40 dark:via-purple-900/40 dark:to-indigo-900/40 rounded-[36px] flex items-center justify-center shadow-2xl shadow-violet-500/15">
                  <Bot size={72} className="text-violet-600 dark:text-violet-400" />
                </div>
                <div className="absolute -top-2 -right-2 w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-xl shadow-orange-500/30 animate-bounce">
                  <Zap size={24} className="text-white" />
                </div>
              </div>

              <h2 className="text-3xl font-bold text-center mb-4 bg-gradient-to-r from-violet-700 to-indigo-700 dark:from-violet-300 dark:to-indigo-300 bg-clip-text text-transparent">
                欢迎回来！
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl text-center mb-10 leading-relaxed">
                我是您的专属学术研究助手。<br/>
                请告诉我您的研究兴趣或问题，我将为您提供专业的解答和论文推荐。
              </p>

              {/* 快速开始建议 */}
              <div className="w-full max-w-2xl space-y-3">
                {[
                  "我想了解深度学习在计算机视觉中的最新应用",
                  "请推荐一些关于Transformer架构的经典论文",
                  "帮我分析一下自然语言处理的当前研究热点",
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(suggestion)}
                    className="group w-full text-left p-4.5 bg-white/80 dark:bg-slate-900/70 backdrop-blur-sm border border-slate-200/70 dark:border-slate-800/60 rounded-2xl hover:border-violet-300/70 dark:hover:border-violet-700/50 hover:shadow-xl hover:shadow-violet-500/10 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-violet-500 to-indigo-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                        <MessageSquare size={20} className="text-white" />
                      </div>
                      <div className="flex-1 pt-0.5">
                        <p className="font-semibold text-slate-900 dark:text-white text-sm leading-snug">
                          {suggestion}
                        </p>
                      </div>
                      <ChevronRight size={18} className="flex-shrink-0 text-slate-400 group-hover:text-violet-500 group-hover:translate-x-1 transition-all opacity-0 group-hover:opacity-100" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* 对话列表 */
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
                  <ProgressIndicator stage={progressStage} message={progressMessage} />
                </div>
              )}

              {isLoading && !progressStage && !isStreaming && (
                <ChatMessage role="assistant" isLoading={true} />
              )}

              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="fixed bottom-28 left-1/2 -translate-x-1/2 z-50 max-w-lg w-full px-4">
              <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-960/60 dark:to-rose-960/60 border border-red-200/60 dark:border-red-800/50 rounded-2xl shadow-2xl backdrop-blur-sm">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                    <span className="text-red-600 dark:text-red-400 text-sm">✕</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-red-900 dark:text-red-100 font-semibold text-sm mb-1">发生错误</p>
                    <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
                    <button 
                      onClick={() => setError(null)} 
                      className="mt-2 text-red-600 dark:text-red-400 text-xs underline"
                    >
                      关闭
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Chat Input */}
      <ChatInput
        onSend={handleSend}
        isLoading={isLoading || isStreaming}
        mode="chat"
        onModeChange={() => {}}
        placeholder="描述您的研究问题或需求..."
      />

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowSettings(false)}>
          <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            
            <div className="sticky top-0 bg-gradient-to-r from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 border-b border-slate-200/50 dark:border-slate-800 p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Settings size={24} className="text-violet-600" />
                  系统设置与偏好
                </h2>
                <button onClick={() => setShowSettings(false)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl">
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              
              {/* 用户信息 */}
              <section className="p-5 bg-gradient-to-br from-violet-50 to-indigo-50 dark:from-violet-950/20 dark:to-indigo-950/20 rounded-xl border border-violet-200/50 dark:border-violet-800/40">
                <h3 className="font-bold text-base text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                  <User size={18} className="text-violet-600" /> 账户信息
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-slate-500">邮箱：</span><span className="font-medium text-slate-900 dark:text-white">{email}</span></div>
                  <div><span className="text-slate-500">用户ID：</span><span className="font-mono text-xs text-slate-700 dark:text-slate-300">{userId.slice(0,8)}...</span></div>
                </div>
                
                {userProfile && (
                  <div className="mt-4">
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 block mb-2">研究方向：</span>
                    <div className="flex flex-wrap gap-2">
                      {(userProfile.interests || []).map((interest, idx) => (
                        <span key={idx} className="px-3 py-1 bg-white dark:bg-slate-800 rounded-full text-xs font-medium text-violet-700 dark:text-violet-300 border border-violet-200/50">
                          {interest}
                        </span>
                      ))}
                      {(userProfile.domains || []).map((domain, idx) => (
                        <span key={`d-${idx}`} className="px-3 py-1 bg-violet-100 dark:bg-violet-900/30 rounded-full text-xs font-medium text-violet-800 dark:text-violet-200">
                          {domain}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </section>

              {/* 调度器控制 */}
              <section className="p-5 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-xl border border-purple-200/50 dark:border-purple-800/40">
                <h3 className="font-bold text-base text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                  <Clock size={18} className="text-purple-600" /> 定时任务调度
                </h3>
                <div className="bg-white/60 dark:bg-slate-800/60 rounded-lg p-4 mb-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">状态：</span>
                      <span className={`font-bold ml-1 ${schedulerStatus?.is_running ? 'text-green-600' : 'text-slate-600'}`}>
                        {schedulerStatus?.is_running ? '运行中' : '已停止'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">配置任务数：</span>
                      <span className="font-bold text-slate-900 dark:text-white ml-1">{schedulerStatus?.configured_tasks || 0}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => apiClient.startScheduler().then(r => r.success && loadSchedulerStatus())} className="flex-1 px-4 py-2.5 bg-green-600 text-white rounded-xl text-sm font-semibold hover:bg-green-700 transition-colors">
                    启动
                  </button>
                  <button onClick={() => apiClient.stopScheduler().then(r => r.success && loadSchedulerStatus())} className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 transition-colors">
                    停止
                  </button>
                  <button onClick={() => apiClient.runPapersNow().then(alert)} className="flex-1 px-4 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-semibold hover:bg-purple-700 transition-colors">
                    推荐测试
                  </button>
                </div>
              </section>

              {/* 邮件服务 */}
              <section className="p-5 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-xl border border-blue-200/50 dark:border-blue-800/40">
                <h3 className="font-bold text-base text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                  <Mail size={18} className="text-blue-600" /> 邮件通知服务
                </h3>
                <button 
                  onClick={() => apiClient.testEmail().then(r => alert(r.success ? '✅ SMTP连接成功' : `❌ ${r.error}`))}
                  className="w-full py-2.5 px-4 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors mb-3"
                >
                  测试SMTP连接
                </button>
                <button 
                  onClick={() => apiClient.sendTestEmail(userId).then(r => alert(r.success ? '✅ 测试邮件已发送' : `❌ ${r.error}`))}
                  className="w-full py-2.5 px-4 bg-cyan-600 text-white rounded-xl text-sm font-semibold hover:bg-cyan-700 transition-colors"
                >
                  发送测试邮件到我的邮箱
                </button>
              </section>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
