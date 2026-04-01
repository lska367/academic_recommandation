
import { User, Bot, FileText, User as UserIcon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { memo } from 'react';

const PaperCard = memo(({ paper, index }) => {
  const metadata = paper.metadata || paper;
  return (
    <div
      className="group relative p-4 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700/50 hover:border-purple-300 dark:hover:border-purple-600/50 hover:shadow-lg hover:shadow-purple-500/5 transition-all duration-200"
    >
      <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-purple-500 to-indigo-500 rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/40 dark:to-indigo-900/40 rounded-lg flex items-center justify-center">
          <FileText size={16} className="text-purple-600 dark:text-purple-400" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h5 className="font-semibold text-slate-900 dark:text-slate-100 text-sm leading-snug group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">
            {metadata.title || '无标题'}
          </h5>
          
          {metadata.authors && (
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5 flex items-center gap-1.5">
              <UserIcon size={12} className="flex-shrink-0" />
              <span className="truncate">{metadata.authors}</span>
            </p>
          )}
          
          {metadata.summary && (
            <p className="text-xs text-slate-500 dark:text-slate-500 mt-2 line-clamp-3 leading-relaxed">
              {metadata.summary}
            </p>
          )}
        </div>
      </div>
    </div>
  );
});

PaperCard.displayName = 'PaperCard';

export const ChatMessage = memo(({ role, content, papers, isLoading }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-4 py-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex gap-4 max-w-3xl ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        <div
          className={`flex-shrink-0 w-11 h-11 rounded-2xl flex items-center justify-center shadow-sm ${
            isUser
              ? 'bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-purple-500/20'
              : 'bg-gradient-to-br from-slate-200 to-slate-300 text-slate-700 dark:from-slate-700 dark:to-slate-600 dark:text-slate-200'
          }`}
        >
          {isUser ? <User size={22} /> : <Bot size={22} />}
        </div>

        <div
          className={`px-5 py-4 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-br from-purple-600 to-indigo-600 text-white rounded-tr-md shadow-lg shadow-purple-500/20'
              : 'bg-white dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 rounded-tl-md shadow-sm border border-slate-200 dark:border-slate-700/50'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2.5 px-2">
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          ) : (
            <>
              {content && (
                <div className={`prose prose-sm max-w-none ${
                  isUser 
                    ? 'prose-invert prose-p:mb-0 prose-p:text-white/95' 
                    : 'dark:prose-invert prose-headings:text-slate-900 dark:prose-headings:text-white prose-p:text-slate-700 dark:prose-p:text-slate-300'
                }`}>
                  <ReactMarkdown
                    components={{
                      h1: ({ ...props }) => <h1 className="text-xl font-bold mb-3 mt-4 first:mt-0" {...props} />,
                      h2: ({ ...props }) => <h2 className="text-lg font-semibold mb-2.5 mt-3 first:mt-0" {...props} />,
                      h3: ({ ...props }) => <h3 className="text-base font-medium mb-2 mt-2.5 first:mt-0" {...props} />,
                      p: ({ ...props }) => <p className="leading-relaxed mb-3 last:mb-0" {...props} />,
                      ul: ({ ...props }) => <ul className="list-disc pl-5 mb-3 last:mb-0 space-y-1.5" {...props} />,
                      ol: ({ ...props }) => <ol className="list-decimal pl-5 mb-3 last:mb-0 space-y-1.5" {...props} />,
                      li: ({ ...props }) => <li className="leading-relaxed" {...props} />,
                      code: ({ ...props }) => <code className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 rounded text-xs font-mono" {...props} />,
                      pre: ({ ...props }) => <pre className="p-3 bg-slate-100 dark:bg-slate-700 rounded-lg text-xs font-mono overflow-x-auto mb-3 last:mb-0" {...props} />,
                      blockquote: ({ ...props }) => <blockquote className="border-l-4 border-purple-300 dark:border-purple-600 pl-4 py-1 my-3 italic text-slate-600 dark:text-slate-400" {...props} />,
                    }}
                  >
                    {content}
                  </ReactMarkdown>
                </div>
              )}

              {papers && papers.length > 0 && (
                <div className="mt-5 pt-4 border-t border-slate-200 dark:border-slate-700/50">
                  <h4 className="font-semibold text-sm text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                    <FileText size={16} className="text-purple-600 dark:text-purple-400" />
                    相关论文 ({papers.length})
                  </h4>
                  <div className="space-y-3">
                    {papers.map((paper, index) => (
                      <PaperCard key={index} paper={paper} index={index} />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
});

ChatMessage.displayName = 'ChatMessage';
