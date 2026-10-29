export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded border border-marigold-600/30 bg-marigold-400/10 px-4 py-3">
      <p className="font-body text-sm text-ink">
        Couldn't load this: {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-sm font-medium text-forest-600 underline underline-offset-2 hover:text-forest-900"
        >
          Try again
        </button>
      )}
    </div>
  )
}
