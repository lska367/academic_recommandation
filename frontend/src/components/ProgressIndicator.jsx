
import { Search, ArrowUpDown, FileText, Loader2 } from 'lucide-react';
import { memo } from 'react';

const STAGE_CONFIG = {
  search_start: {
    icon: Search,
    label: '开始检索',
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
    borderColor: 'border-blue-200 dark:border-blue-800/50',
  },
  query_encoding: {
    icon: Loader2,
    label: '正在编码查询',
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
    borderColor: 'border-blue-200 dark:border-blue-800/50',
  },
  vector_search: {
    icon: Search,
    label: '正在搜索向量库',
    color: 'from-purple-500 to-indigo-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    borderColor: 'border-purple-200 dark:border-purple-800/50',
  },
  vector_search_complete: {
    icon: Search,
    label: '检索完成',
    color: 'from-emerald-500 to-teal-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-950/30',
    borderColor: 'border-emerald-200 dark:border-emerald-800/50',
  },
  rerank_start: {
    icon: ArrowUpDown,
    label: '开始重排序',
    color: 'from-amber-500 to-orange-500',
    bgColor: 'bg-amber-50 dark:bg-amber-950/30',
    borderColor: 'border-amber-200 dark:border-amber-800/50',
  },
  rerank_scoring: {
    icon: Loader2,
    label: '论文打分中',
    color: 'from-amber-500 to-orange-500',
    bgColor: 'bg-amber-50 dark:bg-amber-950/30',
    borderColor: 'border-amber-200 dark:border-amber-800/50',
  },
  rerank_complete: {
    icon: ArrowUpDown,
    label: '重排序完成',
    color: 'from-emerald-500 to-teal-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-950/30',
    borderColor: 'border-emerald-200 dark:border-emerald-800/50',
  },
  report_start: {
    icon: FileText,
    label: '开始生成综述',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    borderColor: 'border-purple-200 dark:border-purple-800/50',
  },
  report_content_start: {
    icon: Loader2,
    label: '正在撰写报告',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    borderColor: 'border-purple-200 dark:border-purple-800/50',
  },
  report_chunk: {
    icon: Loader2,
    label: '撰写中',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    borderColor: 'border-purple-200 dark:border-purple-800/50',
  },
};

export const ProgressIndicator = memo(({ stage, message, progress, total }) => {
  const config = STAGE_CONFIG[stage] || STAGE_CONFIG[stage.split('_')[0] + '_start'] || {
    icon: Loader2,
    label: '处理中',
    color: 'from-slate-500 to-slate-600',
    bgColor: 'bg-slate-50 dark:bg-slate-800/50',
    borderColor: 'border-slate-200 dark:border-slate-700/50',
  };

  const Icon = config.icon;
  const isComplete = stage.includes('complete') || stage.includes('_complete');
  const isLoading = !isComplete && stage !== 'report_chunk';

  const percentage = total > 0 && progress !== undefined
    ? Math.round((progress / total) * 100)
    : null;

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl border ${config.borderColor} ${config.bgColor} transition-all duration-300`}>
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-sm`}>
        <Icon size={20} className={isLoading ? 'animate-spin' : ''} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium text-sm text-slate-900 dark:text-slate-100">
            {config.label}
          </span>
          {percentage !== null && (
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
              {progress}/{total} ({percentage}%)
            </span>
          )}
        </div>

        {message && (
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 truncate">
            {message}
          </p>
        )}

        {percentage !== null && !isComplete && (
          <div className="mt-2 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${config.color} rounded-full transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
});

ProgressIndicator.displayName = 'ProgressIndicator';

export default ProgressIndicator;
