const NEAR_ZERO_CONTRIBUTION_THRESHOLD = 0.05;

export function formatContributionDisplay(value, digits = 2) {
  if (value == null || typeof value !== "number") {
    return value == null ? "null" : String(value);
  }

  if (Math.abs(value) < NEAR_ZERO_CONTRIBUTION_THRESHOLD) {
    return "≈0";
  }

  return value.toFixed(digits);
}
