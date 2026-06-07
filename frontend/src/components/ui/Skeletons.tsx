export function SkeletonCard() {
  return (
    <div className="glass-card p-6 space-y-4">
      <div className="skeleton h-4 w-3/4 rounded" />
      <div className="skeleton h-3 w-1/2 rounded" />
      <div className="skeleton h-3 w-full rounded" />
      <div className="skeleton h-3 w-2/3 rounded" />
    </div>
  );
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 p-4">
      <div className="skeleton h-10 w-10 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="skeleton h-3 w-1/3 rounded" />
        <div className="skeleton h-3 w-2/3 rounded" />
      </div>
    </div>
  );
}

export function SkeletonStat() {
  return (
    <div className="glass-card p-6 space-y-3">
      <div className="skeleton h-4 w-1/2 rounded" />
      <div className="skeleton h-8 w-1/3 rounded" />
      <div className="skeleton h-2 w-full rounded" />
    </div>
  );
}
