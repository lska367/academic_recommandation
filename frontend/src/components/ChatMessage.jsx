
import { User, Bot, FileText, User as UserIcon, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { memo, useEffect, useState } from 'react';

const PaperCard = memo(({ paper, index }) => {
  const metadata = paper.metadata || paper;
  const arxivUrl = metadata.arxiv_url || `https://arxiv.org/abs/${metadata.paper_id || ''}`;

  const handleClick = (e) => {
    e.stopPropagation();
    if (arxivUrl && arxivUrl !== 'https://arxiv.org/abs/') {
      window.open(arxivUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div
      onClick={handleClick}
      className="group relative p-4 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700/50 hover:border-purple-300 dark:hover:border-purple-600/50 hover:shadow-lg hover:shadow-purple-500/5 transition-all duration-200 cursor-pointer"
    >
      <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-purple-500 to-indigo-500 rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/40 dark:to-indigo-900/40 rounded-lg flex items-center justify-center">
          <FileText size={16} className="text-purple-600 dark:text-purple-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h5 className="font-semibold text-slate-900 dark:text-slate-100 text-sm leading-snug group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">
              {metadata.title || '无标题'}
            </h5>
            <ExternalLink size={14} className="flex-shrink-0 text-slate-400 group-hover:text-purple-500 opacity-0 group-hover:opacity-100 transition-opacity mt-0.5" />
          </div>

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

          {paper.rerank_score !== undefined && (
            <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-amber-50 dark:bg-amber-950/30 rounded-lg text-xs font-medium text-amber-700 dark:text-amber-400">
              <span>相关度评分:</span>
              <span className="font-bold">{paper.rerank_score?.toFixed(1) || '-'}/10</span>
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-700/50 flex items-center justify-between">
        <span className="text-xs text-purple-500 dark:text-purple-400 font-medium group-hover:text-purple-600 dark:group-hover:text-purple-300 transition-colors">
          点击查看论文详情 →
        </span>
        <span className="text-[10px] text-slate-400 dark:text-slate-500">
          arXiv
        </span>
      </div>
    </div>
  );
});

PaperCard.displayName = 'PaperCard';

const TypingCursor = memo(() => (
  <span className="inline-block w-2 h-5 bg-purple-600 dark:bg-purple-400 ml-1 animate-pulse align-middle" />
));

TypingCursor.displayName = 'TypingCursor';

export const ChatMessage = memo(({ role, content, papers, isLoading, isStreaming, streamingContent }) => {
  const isUser = role === 'user';
  const [displayedContent, setDisplayedContent] = useState('');
  const [showCursor, setShowCursor] = useState(false);

  useEffect(() => {
    if (isStreaming && streamingContent) {
      setDisplayedContent(streamingContent);
      setShowCursor(true);
    } else if (content) {
      setDisplayedContent(content);
      setShowCursor(false);
    } else {
      setDisplayedContent('');
      setShowCursor(false);
    }
  }, [content, isStreaming, streamingContent]);

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
          {isLoading && !isStreaming ? (
            <div className="flex items-center gap-2.5 px-2">
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2.5 h-2.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          ) : (
            <>
              {displayedContent && (
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
                    {displayedContent}
                  </ReactMarkdown>
                  {showCursor && <TypingCursor />}
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
