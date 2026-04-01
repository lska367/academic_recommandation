
import { useState, useCallback } from 'react';
import { Send, Sparkles, Search } from 'lucide-react';

const MODE_CONFIG = {
  search: { icon: Search, label: '论文检索' },
  survey: { icon: Sparkles, label: '学术综述' },
};

export const ChatInput = ({ onSend, isLoading, mode, onModeChange, placeholder }) => {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim(), mode);
      setInput('');
    }
  }, [input, isLoading, mode, onSend]);

  const currentModeConfig = MODE_CONFIG[mode];

  return (
    <div className="border-t border-slate-200/70 dark:border-slate-800/70 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl px-6 py-5">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="flex bg-slate-100 dark:bg-slate-800/70 p-1.5 rounded-2xl border border-slate-200/60 dark:border-slate-700/50">
              {Object.entries(MODE_CONFIG).map(([key, config]) => {
                const Icon = config.icon;
                const isActive = mode === key;
                return (
                  <button
                    key={key}
                    onClick={() => onModeChange(key)}
                    className={`
                      flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200
                      ${isActive 
                        ? 'bg-white dark:bg-slate-700 text-purple-700 dark:text-purple-200 shadow-sm ring-1 ring-purple-200/50 dark:ring-purple-500/30' 
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'}
                    `}
                  >
                    <Icon size={17} />
                    {config.label}
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="flex gap-4 items-end">
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <currentModeConfig.icon size={20} className="text-slate-400 dark:text-slate-500" />
              </div>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={placeholder || (
                  mode === 'search'
                    ? '输入研究主题，如：深度学习在计算机视觉中的应用...'
                    : '输入研究主题，如：自然语言处理的最新进展...'
                )}
                disabled={isLoading}
                className="
                  w-full pl-12 pr-4 py-4 text-base 
                  bg-slate-100 dark:bg-slate-800/80 
                  border-2 border-slate-200/70 dark:border-slate-700/60 
                  rounded-2xl 
                  focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400 dark:focus:border-purple-500 
                  dark:text-white 
                  disabled:opacity-60 disabled:cursor-not-allowed 
                  transition-all duration-200
                  placeholder:text-slate-500 dark:placeholder:text-slate-500
                "
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="
                flex items-center gap-2 px-6 py-4 
                bg-gradient-to-r from-purple-600 to-indigo-600 
                text-white rounded-2xl 
                hover:from-purple-700 hover:to-indigo-700 
                focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:ring-offset-2 
                disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-purple-600 disabled:hover:to-indigo-600 
                transition-all duration-200 
                shadow-lg shadow-purple-500/20 
                hover:shadow-xl hover:shadow-purple-500/30
                active:scale-95
              "
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span className="font-semibold">处理中</span>
                </>
              ) : (
                <>
                  <Send size={20} />
                  <span className="font-semibold">发送</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
