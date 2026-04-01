import { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';

export const ChatInput = ({ onSend, isLoading, mode, onModeChange }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim(), mode);
      setInput('');
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => onModeChange('search')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === 'search'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            论文检索
          </button>
          <button
            onClick={() => onModeChange('survey')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors flex items-center gap-1 ${
              mode === 'survey'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <Sparkles size={16} />
            学术综述
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              mode === 'search'
                ? '输入研究主题或关键词，查找相关论文...'
                : '输入研究主题，生成学术综述报告...'
            }
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send size={20} />
            发送
          </button>
        </form>
      </div>
    </div>
  );
};
