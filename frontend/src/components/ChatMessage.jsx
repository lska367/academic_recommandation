import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const ChatMessage = ({ role, content, papers, isLoading }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-3 py-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex gap-3 max-w-3xl ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200'
          }`}
        >
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>

        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-purple-600 text-white rounded-tr-none'
              : 'bg-gray-100 text-gray-900 rounded-tl-none dark:bg-gray-800 dark:text-gray-100'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          ) : (
            <>
              {content && (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{content}</ReactMarkdown>
                </div>
              )}

              {papers && papers.length > 0 && (
                <div className="mt-4 space-y-3">
                  <h4 className="font-semibold text-sm mb-2">相关论文：</h4>
                  {papers.map((paper, index) => {
                    const metadata = paper.metadata || paper;
                    return (
                      <div
                        key={index}
                        className="p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                      >
                        <h5 className="font-medium text-sm text-purple-700 dark:text-purple-400">
                          {metadata.title || '无标题'}
                        </h5>
                        {metadata.authors && (
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            {metadata.authors}
                          </p>
                        )}
                        {metadata.summary && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 line-clamp-2">
                            {metadata.summary}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
