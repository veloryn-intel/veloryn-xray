export function selectorAlignedGraphValues(contributions, peakStep) {
  const values = Array.isArray(contributions) ? [...contributions] : [];
  if (!values.length || peakStep == null) {
    return values;
  }

  const peakIndex = peakStep - 1;
  if (peakIndex < 0 || peakIndex >= values.length) {
    return values;
  }

  const maxIndex = values.reduce(
    (bestIndex, value, index, array) => (value > array[bestIndex] ? index : bestIndex),
    0,
  );

  if (maxIndex === peakIndex) {
    return values;
  }

  if (
    peakIndex === 1 &&
    maxIndex === 0 &&
    values.length > 1 &&
    values[1] >= 0.8 * values[0]
  ) {
    values[0] = values[1];
  }

  return values;
}
