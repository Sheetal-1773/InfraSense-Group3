interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export function Skeleton({ className = '', variant = 'rectangular', width, height }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200'
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  }

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={{ width, height }}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Skeleton variant="circular" width={20} height={20} />
        <Skeleton width={80} height={16} />
      </div>
      <Skeleton width="60%" height={32} className="mb-2" />
      <Skeleton height={6} className="mb-2" />
      <div className="flex justify-between">
        <Skeleton width={60} height={12} />
        <Skeleton width={50} height={12} />
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      <div className="flex gap-4 p-4 bg-[#F7F7F7] rounded-lg">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} height={16} className="flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 border-b border-[#E5E5E5]">
          {[1, 2, 3, 4, 5].map((j) => (
            <Skeleton key={j} height={16} className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
      <Skeleton width={150} height={20} className="mb-4" />
      <Skeleton height={200} />
    </div>
  )
}