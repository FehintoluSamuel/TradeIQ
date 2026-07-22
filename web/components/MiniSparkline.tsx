export function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return null;
  const width = 100;
  const height = 32;
  const min = Math.min(...data);
  const max = Math.min(...data) === Math.max(...data) ? min + 1 : Math.max(...data);
  const range = max - min;
  const step = width / (data.length - 1);
  const points = data
    .map((v, i) => `${i * step},${height - ((v - min) / range) * height}`)
    .join(' ');

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <polyline points={points} fill="none" stroke={color} strokeWidth={2} />
    </svg>
  );
}
