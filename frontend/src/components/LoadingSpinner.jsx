export default function LoadingSpinner({ label = 'Loading' }) {
  return (
    <div className="flex items-center gap-3 py-8 text-forest-600">
      <span
        className="h-5 w-5 animate-spin rounded-full border-2 border-forest-100 border-t-forest-600"
        aria-hidden="true"
      />
      <span className="font-body text-sm">{label}</span>
    </div>
  )
}
