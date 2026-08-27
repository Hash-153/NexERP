import React from 'react';

export interface KanbanCard {
  id: string;
  title: string;
  subtitle?: string;
  tag: string;
  score?: number;
  owner?: string;
  date?: string;
}

export interface KanbanColumn {
  id: string;
  title: string;
  color: string;
  cards: KanbanCard[];
}

interface KanbanWorkflowBoardProps {
  columns: KanbanColumn[];
  onCardClick?: (card: KanbanCard) => void;
}

export function KanbanWorkflowBoard({ columns, onCardClick }: KanbanWorkflowBoardProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {columns.map(col => (
        <div key={col.id} className="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-col max-h-[750px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800 mb-3">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${col.color}`}></span>
              <h4 className="font-bold text-slate-800 dark:text-slate-200 text-sm">{col.title}</h4>
            </div>
            <span className="bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs px-2 py-0.5 rounded-full font-bold">
              {col.cards.length}
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto flex-1 pr-1">
            {col.cards.map(card => (
              <div
                key={card.id}
                onClick={() => onCardClick && onCardClick(card)}
                className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 shadow-sm hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 cursor-pointer transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400">
                    {card.tag}
                  </span>
                  {card.score !== undefined && (
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                      ★ {card.score}
                    </span>
                  )}
                </div>
                <h5 className="font-semibold text-slate-900 dark:text-white text-sm leading-tight">{card.title}</h5>
                {card.subtitle && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{card.subtitle}</p>
                )}
                <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                  <span>{card.owner || 'Unassigned'}</span>
                  <span>{card.date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
