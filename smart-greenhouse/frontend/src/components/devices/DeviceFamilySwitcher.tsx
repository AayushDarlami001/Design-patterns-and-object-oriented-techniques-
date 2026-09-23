type DeviceFamily = "simulation" | "edge";

type Props = {
  selectedFamily: DeviceFamily;
  onChange: (family: DeviceFamily) => void;
};

export default function DeviceFamilySwitcher({
  selectedFamily,
  onChange,
}: Props) {
  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        className={`rounded px-3 py-2 text-sm ${
          selectedFamily === "simulation"
            ? "bg-green-600 text-white"
            : "bg-gray-200 text-gray-700"
        }`}
      >
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        className={`rounded px-3 py-2 text-sm ${
          selectedFamily === "edge"
            ? "bg-green-600 text-white"
            : "bg-gray-200 text-gray-700"
        }`}
      >
        Edge
      </button>
    </div>
  );
}