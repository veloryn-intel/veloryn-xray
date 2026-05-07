import {
  CartesianGrid,
  Dot,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatContributionDisplay } from "../utils/formatContributionDisplay";

function ChartDot(props) {
  const { cx, cy, payload, peakStep } = props;

  if (cx == null || cy == null) {
    return null;
  }

  const isPeak = payload.label === "Peak";
  const isPostPeak = payload.step > peakStep;

  return (
    <Dot
      cx={cx}
      cy={cy}
      r={isPeak ? 6 : 3.5}
      fill={isPeak ? "var(--accent-gold)" : "#6B7280"}
      stroke={isPeak ? "var(--accent-gold)" : "#6B7280"}
      strokeWidth={isPeak ? 2 : 1}
      fillOpacity={isPostPeak ? 0.45 : 1}
    />
  );
}

function GraphTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;

  return (
    <div className="rounded-lg border border-border bg-surface px-3 py-2 text-xs text-text-primary shadow-card">
      <div>Step {point.step}</div>
      <div className="text-text-secondary">{point.label}</div>
      <div className="mt-1 text-text-primary">{formatContributionDisplay(point.value)}</div>
    </div>
  );
}

export default function Graph({ data, peakStep }) {
  const stepValues = data.map((point) => point.step);
  const minStep = stepValues.length ? Math.min(...stepValues) : 1;
  const maxStep = stepValues.length ? Math.max(...stepValues) : peakStep;
  const chartData = data.map((point) => ({
    ...point,
    prePeak: point.step <= peakStep ? point.value : null,
    postPeak: point.step >= peakStep ? point.value : null,
  }));

  return (
    <section className="rounded-2xl border border-border bg-surface p-4 shadow-card sm:p-5">
      <div className="mb-3 text-center text-sm font-medium text-text-primary">
        Peak at Step {peakStep}
      </div>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 16, right: 16, bottom: 28, left: 8 }}
            style={{ background: "transparent" }}
          >
            <CartesianGrid vertical={false} stroke="#1A1C1F" strokeOpacity={0.3} />
            <XAxis
              dataKey="step"
              type="number"
              domain={[minStep, maxStep]}
              ticks={stepValues}
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#E8EAF0", fontSize: 13 }}
              label={{
                value: "Step",
                position: "insideBottom",
                offset: -10,
                fill: "#E8EAF0",
                fontSize: 12,
              }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#E8EAF0", fontSize: 13 }}
              width={72}
              tickFormatter={(value) => formatContributionDisplay(value)}
              label={{
                value: "Improvement per step",
                angle: -90,
                position: "insideLeft",
                offset: -2,
                fill: "#E8EAF0",
                fontSize: 12,
                style: { textAnchor: "middle" },
              }}
            />
            <Tooltip content={<GraphTooltip />} cursor={false} />
            <ReferenceLine
              x={peakStep}
              stroke="var(--accent-gold)"
              strokeDasharray="4 4"
              strokeOpacity={0.8}
            />
            <Line
              type="monotone"
              dataKey="prePeak"
              stroke="#6B7280"
              strokeWidth={2}
              dot={(props) => <ChartDot {...props} peakStep={peakStep} />}
              connectNulls
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="postPeak"
              stroke="#6B7280"
              strokeWidth={2}
              strokeOpacity={0.45}
              dot={(props) => <ChartDot {...props} peakStep={peakStep} />}
              connectNulls
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
