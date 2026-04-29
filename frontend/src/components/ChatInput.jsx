
import { useState, useCallback } from 'react';
import { Send, Sparkles, Mic } from 'lucide-react';

export const ChatInput = ({ onSend, isLoading, mode, onModeChange, placeholder }) => {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  }, [input, isLoading, onSend]);

  return (
    <div className="border-t border-slate-200/70 dark:border-slate-800/70 bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl px-6 py-5">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="flex gap-4 items-end">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Sparkles size={20} className="text-violet-400 dark:text-violet-500" />
            </div>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder || "描述您的研究兴趣或问题..."}
              disabled={isLoading}
              className="
                w-full pl-12 pr-4 py-4 text-base 
                bg-slate-100/80 dark:bg-slate-800/80 
                border-2 border-slate-200/70 dark:border-slate-700/60 
                rounded-2xl 
                focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-400 dark:focus:border-violet-500 
                dark:text-white 
                disabled:opacity-60 disabled:cursor-not-allowed 
                transition-all duration-200
                placeholder:text-slate-500 dark:placeholder:text-slate-500
                shadow-inner
              "
            />
          </div>
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="
              flex items-center gap-2.5 px-7 py-4 
              bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 
              text-white rounded-2xl 
              hover:from-violet-700 hover:via-purple-700 hover:to-indigo-700 
              focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:ring-offset-2 
              disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-violet-600 disabled:hover:via-purple-600 disabled:hover:to-indigo-600 
              transition-all duration-200 
              shadow-lg shadow-violet-500/25 
              hover:shadow-xl hover:shadow-violet-500/30
              active:scale-95
              font-semibold
            "
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>思考中</span>
              </>
            ) : (
              <>
                <Send size={19} />
                <span>发送</span>
              </>
            )}
          </button>
        </form>

        {/* Helper Text */}
        <div className="mt-3 flex items-center justify-center gap-2 text-xs text-slate-500">
          <Sparkles size={12} className="text-violet-400" />
          <span>按 Enter 发送 · 系统将自动分析您的问题并生成个性化推荐</span>
        </div>
      </div>
    </div>
  );
};
