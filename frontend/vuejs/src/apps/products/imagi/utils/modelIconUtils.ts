import type { AIModel } from '@/apps/products/imagi/types';

export const getModelTypeClass = (model: AIModel): string => {
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  if (modelType === 'anthropic') {
    return 'bg-gradient-to-br from-blue-600/20 to-indigo-600/20 text-blue-400 border border-blue-500/20';
  } else if (modelType === 'openai') {
    return 'bg-gradient-to-br from-emerald-600/20 to-green-600/20 text-emerald-400 border border-emerald-500/20';
  }
  if (model.id === 'claude-sonnet-4-20250514') {
    return 'bg-gradient-to-br from-primary-600/20 to-violet-600/20 text-primary-400 border border-primary-500/20';
  }
  return 'bg-gradient-to-br from-gray-600/20 to-gray-700/20 text-gray-400 border border-gray-500/20';
}

export const getModelTypeIcon = (model: AIModel): string => {
  // DRY: Claude Sonnet 3.7 and GPT-4.1 variants use the same icon logic
  if (
    model.id === 'claude-sonnet-4-20250514' ||
    (model.id && (model.id.includes('gpt-4-1106') || model.id.includes('gpt-4-0125')))
  ) {
    return 'fa-brain';
  }
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  if (modelType === 'anthropic') {
    return 'fa-diamond';
  } else if (modelType === 'openai') {
    return 'fa-bolt';
  }
  return 'fa-robot';
}
