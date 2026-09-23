import { useEffect, useState } from "react";

import {
  getDevices,
  provisionDeviceFamily,
  type DeviceDto,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

type DeviceFamily = "simulation" | "edge";

export default function DeviceList() {
  const [family, setFamily] = useState<DeviceFamily>("simulation");
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
  const [error, setError] = useState("");

  async function loadDevices(selectedFamily: DeviceFamily) {
    try {
      setLoading(true);
      setError("");

      const data = await getDevices(selectedFamily);
      setDevices(data);
    } catch {
      setError("Could not load devices.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices(family);
  }, [family]);

  async function handleProvision() {
    try {
      setProvisioning(true);
      setError("");

      await provisionDeviceFamily(family);

      await loadDevices(family);
    } catch {
      setError("Could not provision device family.");
    } finally {
      setProvisioning(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <DeviceFamilySwitcher
          selectedFamily={family}
          onChange={setFamily}
        />

        <button
          type="button"
          onClick={handleProvision}
          disabled={provisioning}
          className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {provisioning
            ? "Provisioning..."
            : `Provision ${family} kit`}
        </button>
      </div>

      {loading && (
        <p className="text-sm text-gray-500">
          Loading devices...
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}

      {!loading && !error && devices.length === 0 && (
        <p className="text-sm text-gray-500">
          No devices for this family yet.
        </p>
      )}

      <div className="space-y-2">
        {devices.map((device) => (
          <div
            key={device.id}
            className="rounded border p-3"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-medium">
                  {device.display_name}
                </p>

                <p className="text-sm text-gray-500">
                  {device.device_type}
                </p>
              </div>

              <div className="flex gap-2">
                <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                  {device.device_family}
                </span>

                <span
                  className={`rounded px-2 py-1 text-xs ${
                    device.role === "sensor"
                      ? "bg-green-100 text-green-700"
                      : "bg-orange-100 text-orange-700"
                  }`}
                >
                  {device.role}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}