import { AIGenerateCVResponse } from '../../types/ai'

interface AiGeneratePanelsProps {
  result: AIGenerateCVResponse
}

export default function AiGeneratePanels({ result }: AiGeneratePanelsProps) {
  return (
    <div className="space-y-4">
      {result.summary.length ? (
        <div className="rounded-md border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800 dark:border-gray-800 dark:bg-gray-950 dark:text-gray-100">
          <div className="mb-2 font-medium">Summary</div>
          <ul className="list-disc space-y-1 pl-5">
            {result.summary.map(line => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {result.questions.length ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100">
          <div className="mb-2 font-medium">Questions</div>
          <ul className="list-disc space-y-1 pl-5">
            {result.questions.map(line => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}
