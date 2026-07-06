/** Abstract mascot — Taxora-style genie lamp silhouette in brand green */
export function GenieMascot({ className = "size-48 sm:size-56" }: { className?: string }) {
  return (
    <div
      className={`relative inline-flex select-none ${className}`}
      aria-hidden
    >
      <div className="absolute inset-0 rounded-full bg-primary/10 blur-2xl" />
      <svg
        viewBox="0 0 200 200"
        fill="none"
        className="relative z-10 h-full w-full drop-shadow-sm"
        xmlns="http://www.w3.org/2000/svg"
      >
        <ellipse cx="100" cy="168" rx="52" ry="10" fill="oklch(0.38 0.12 158 / 0.15)" />
        <path
          d="M68 148c8-42 24-72 32-88 4-8 12-8 16 0 8 16 24 46 32 88H68z"
          fill="oklch(0.38 0.12 158)"
        />
        <path
          d="M84 60c12-28 20-40 16-48-6-12-28-4-32 8-6 18 4 36 16 40z"
          fill="oklch(0.55 0.14 158)"
        />
        <circle cx="100" cy="44" r="18" fill="oklch(0.7 0.17 158)" />
        <circle cx="94" cy="40" r="4" fill="white" opacity="0.9" />
        <circle cx="106" cy="40" r="4" fill="white" opacity="0.9" />
        <path
          d="M92 50q8 6 16 0"
          stroke="oklch(0.22 0.05 158)"
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M100 26c-8-14-2-22 8-18 6 2 10 12 4 20"
          stroke="oklch(0.55 0.14 158)"
          strokeWidth="3"
          strokeLinecap="round"
          fill="none"
        />
      </svg>
    </div>
  );
}
