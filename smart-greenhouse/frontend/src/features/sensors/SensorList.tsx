import { useEffect, useState } from "react";
import {
  createSensor,
  getSensors,
  type Sensor,
} from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadSensors() {
    try {
      setError("");
      const data = await getSensors();
      setSensors(data);
    } catch {
      setError("Could not load sensors.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  async function addSensor(type: "moisture" | "light") {
    try {
      setError("");
      await createSensor(type);
      await loadSensors();
    } catch {
      setError("Could not add sensor.");
    }
  }

  return (
    <section id="sensors" className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Sensors</h3>

      <div className="mb-4 flex gap-2">
        <button
          onClick={() => addSensor("moisture")}
          className="rounded bg-green-600 px-3 py-2 text-sm text-white"
        >
          Add Moisture
        </button>

        <button
          onClick={() => addSensor("light")}
          className="rounded bg-blue-600 px-3 py-2 text-sm text-white"
        >
          Add Light
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading sensors...</p>}

      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && sensors.length === 0 && (
        <p className="text-gray-500">No sensors added yet.</p>
      )}

      {!loading && !error && sensors.length > 0 && (
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <div key={sensor.id} className="rounded border p-3">
              <p className="font-medium">{sensor.display_name}</p>
              <p className="text-sm text-gray-500">{sensor.device_type}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}