export function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[#F5F6FA] dark:bg-[#12211A] rounded-xl p-3">
      <p className="text-[10px] text-[#8A8FA3] dark:text-[#8FA396] mb-1">{label}</p>
      <p className="text-sm font-semibold">{value}</p>
    </div>
  );
}
