import type { JudgeValidationFile } from "@/lib/types";

export function TrustBanner({
  validation,
}: {
  validation: JudgeValidationFile;
}) {
  const kappa = validation.agreement.cohens_kappa;
  const minKappa = validation.agreement.min_kappa_required;
  const passes = validation.agreement.passes_threshold;
  const untrustworthy = kappa !== null && kappa < minKappa;

  return (
    <div
      className={`border px-4 py-3 text-sm ${
        untrustworthy
          ? "border-red-600 bg-red-50"
          : passes
            ? "border-green-700 bg-green-50"
            : "border-amber-600 bg-amber-50"
      }`}
    >
      <div className="font-semibold text-neutral-900">
        Judge validation:{" "}
        {kappa !== null ? (
          <span className="font-mono">κ = {kappa.toFixed(3)}</span>
        ) : (
          <span className="text-neutral-600">κ unavailable</span>
        )}
        {" · "}
        {passes ? (
          <span className="text-green-800">PASS</span>
        ) : (
          <span className="text-red-800">FAIL</span>
        )}
        <span className="font-normal text-neutral-600">
          {" "}
          (threshold κ ≥ {minKappa.toFixed(1)})
        </span>
      </div>
      <p className="text-xs text-neutral-700 mt-1 font-mono">
        n={validation.agreement.n_scored}/{validation.agreement.n_sampled} scored
        {validation.agreement.accuracy !== null && (
          <> · accuracy={validation.agreement.accuracy.toFixed(3)}</>
        )}
      </p>
      {untrustworthy && (
        <p className="text-xs text-red-900 mt-2 font-medium">
          Warning: judge κ is below {minKappa.toFixed(1)}. Adjudicated span
          metrics and judge-backed verdicts are not trustworthy for this run.
        </p>
      )}
      {!passes && kappa !== null && kappa >= minKappa && (
        <p className="text-xs text-amber-900 mt-2">
          Judge validation did not pass despite κ above threshold — check
          validation.json for details.
        </p>
      )}
    </div>
  );
}
