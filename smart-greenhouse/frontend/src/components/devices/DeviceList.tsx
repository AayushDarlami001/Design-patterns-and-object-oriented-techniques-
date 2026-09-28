import { useEffect, useState } from "react";

import {
  assignDeviceToZone,
  getDevices,
  getLocationConfig,
  getLocations,
  provisionDeviceFamily,
  type DeviceDto,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

type DeviceFamily = "simulation" | "edge";

type ZoneOption = {
  locationId: string;
  locationName: string;
  zoneId: string;
  zoneName: string;
};

export default function DeviceList() {
  const [family, setFamily] =
    useState<DeviceFamily>("simulation");

  const [devices, setDevices] =
    useState<DeviceDto[]>([]);

  const [zoneOptions, setZoneOptions] =
    useState<ZoneOption[]>([]);

  const [loading, setLoading] = useState(true);
  const [provisioning, setProvisioning] =
    useState(false);

  const [assigningId, setAssigningId] =
    useState<string | null>(null);

  const [error, setError] = useState("");

  async function loadDevices(
    selectedFamily: DeviceFamily,
  ) {
    try {
      setLoading(true);
      setError("");

      const data = await getDevices(
        selectedFamily,
      );

      setDevices(data);
    } catch {
      setError("Could not load devices.");
    } finally {
      setLoading(false);
    }
  }

  async function loadZoneOptions() {
    try {
      const locations = await getLocations();

      const configs = await Promise.all(
        locations.map((location) =>
          getLocationConfig(location.id),
        ),
      );

      const options: ZoneOption[] = [];

      for (const config of configs) {
        for (const zone of config.zones) {
          options.push({
            locationId: config.location.id,
            locationName: config.location.name,
            zoneId: zone.id,
            zoneName: zone.name,
          });
        }
      }

      setZoneOptions(options);
    } catch {
      setZoneOptions([]);
    }
  }

  useEffect(() => {
    loadDevices(family);
  }, [family]);

  useEffect(() => {
    loadZoneOptions();
  }, []);

  async function handleProvision() {
    try {
      setProvisioning(true);
      setError("");

      await provisionDeviceFamily(family);

      await loadDevices(family);
    } catch {
      setError(
        "Could not provision device family.",
      );
    } finally {
      setProvisioning(false);
    }
  }

  async function handleZoneChange(
    deviceId: string,
    zoneId: string,
  ) {
    try {
      setAssigningId(deviceId);
      setError("");

      await assignDeviceToZone(
        deviceId,
        zoneId || null,
      );

      await loadDevices(family);
      await loadZoneOptions();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not assign device.",
      );
    } finally {
      setAssigningId(null);
    }
  }

  function currentZoneLabel(
    device: DeviceDto,
  ) {
    if (!device.zone_id) {
      return "Unassigned";
    }

    const zone = zoneOptions.find(
      (option) =>
        option.zoneId === device.zone_id,
    );

    if (!zone) {
      return "Unassigned";
    }

    return `${zone.locationName} — ${zone.zoneName}`;
  }

  const locationGroups = Array.from(
    new Map(
      zoneOptions.map((option) => [
        option.locationId,
        option.locationName,
      ]),
    ),
  );

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
        <p className="rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {!loading &&
        !error &&
        devices.length === 0 && (
          <p className="text-sm text-gray-500">
            No devices for this family yet.
          </p>
        )}

      <div className="space-y-3">
        {devices.map((device) => (
          <div
            key={device.id}
            className="rounded border p-3"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
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

            <div className="mt-3">
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Zone
              </label>

              <select
                value={device.zone_id ?? ""}
                disabled={
                  assigningId === device.id
                }
                onChange={(event) =>
                  handleZoneChange(
                    device.id,
                    event.target.value,
                  )
                }
                className="w-full rounded border px-3 py-2 text-sm"
              >
                <option value="">
                  Unassigned
                </option>

                {locationGroups.map(
                  ([locationId, locationName]) => (
                    <optgroup
                      key={locationId}
                      label={locationName}
                    >
                      {zoneOptions
                        .filter(
                          (option) =>
                            option.locationId ===
                            locationId,
                        )
                        .map((option) => (
                          <option
                            key={option.zoneId}
                            value={option.zoneId}
                          >
                            {option.locationName} —{" "}
                            {option.zoneName}
                          </option>
                        ))}
                    </optgroup>
                  ),
                )}
              </select>

              <p className="mt-1 text-xs text-gray-500">
                {assigningId === device.id
                  ? "Updating..."
                  : currentZoneLabel(device)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}