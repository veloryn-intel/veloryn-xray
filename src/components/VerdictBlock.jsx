export default function VerdictBlock({ verdict, waste, why }) {
  const wastePercent = typeof waste === "string" ? waste.match(/\d+/)?.[0] : waste;
  const wasteLine = wastePercent
    ? `${wastePercent}% of execution after this point was waste.`
    : waste;

  return (
    <section className="space-y-3">
      <div className="max-w-3xl text-2xl font-semibold leading-tight sm:text-3xl">
        {verdict}
      </div>

      <p className="text-lg text-gray-300">{wasteLine}</p>

      <div className="text-sm text-text-secondary">{why}</div>
    </section>
  );
}
