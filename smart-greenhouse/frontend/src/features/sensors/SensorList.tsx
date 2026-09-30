import { useEffect, useState } from "react";

import {
  createSensor,
  getDevices,
  getSensorReadings,
  readSensor,
  updateDeviceSampling,
  type DeviceDto,
  type ReadingDto,
} from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<DeviceDto[]>([]);
  const [latestReadings, setLatestReadings] = useState<
    Record<string, ReadingDto | null>
  >({});
  const [intervalValues, setIntervalValues] = useState<
    Record<string, string>
  >({});
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function loadSensors() {
    try {
      setLoading(true);
      setError("");

      const data = await getDevices(
        undefined,
        "sensor",
      );

      setSensors(data);

      setIntervalValues((current) => {
        const next = { ...current };

        for (const sensor of data) {
          if (next[sensor.id] === undefined) {
            next[sensor.id] = String(
              sensor.sampling_interval_seconds,
            );
          }
        }

        return next;
      });

      return data;
    } catch {
      setError("Could not load sensors.");
      return [];
    } finally {
      setLoading(false);
    }
  }

  async function loadLatestReadings(
    currentSensors: DeviceDto[],
  ) {
    const entries = await Promise.all(
      currentSensors.map(async (sensor) => {
        try {
          const readings = await getSensorReadings(
            sensor.id,
            1,
          );

          return [
            sensor.id,
            readings.length > 0
              ? readings[0]
              : null,
          ] as const;
        } catch {
          return [
            sensor.id,
            null,
          ] as const;
        }
      }),
    );

    setLatestReadings(
      Object.fromEntries(entries),
    );
  }

  useEffect(() => {
    async function start() {
      const data = await loadSensors();
      await loadLatestReadings(data);
    }

    start();
  }, []);

  useEffect(() => {
    if (sensors.length === 0) {
      return;
    }

    const timer = window.setInterval(() => {
      loadLatestReadings(sensors);
    }, 4000);

    return () => {
      window.clearInterval(timer);
    };
  }, [sensors]);

  async function handleAddSensor(
    type: "moisture" | "light",
  ) {
    try {
      setError("");

      await createSensor(type);

      const data = await loadSensors();
      await loadLatestReadings(data);
    } catch {
      setError("Could not add sensor.");
    }
  }

  async function handleReadNow(
    sensor: DeviceDto,
  ) {
    try {
      setBusyId(sensor.id);
      setError("");

      const reading = await readSensor(
        sensor.id,
      );

      setLatestReadings((current) => ({
        ...current,
        [sensor.id]: reading,
      }));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not read sensor.",
      );
    } finally {
      setBusyId(null);
    }
  }

  async function handleSaveInterval(
    sensor: DeviceDto,
  ) {
    const interval = Number(
      intervalValues[sensor.id],
    );

    if (
      !Number.isInteger(interval) ||
      interval < 5
    ) {
      setError(
        "Sampling interval must be at least 5 seconds.",
      );
      return;
    }

    try {
      setBusyId(sensor.id);
      setError("");

      const updated =
        await updateDeviceSampling(
          sensor.id,
          interval,
          sensor.tracking_enabled,
        );

      setSensors((current) =>
        current.map((item) =>
          item.id === updated.id
            ? updated
            : item,
        ),
      );

      setIntervalValues((current) => ({
        ...current,
        [updated.id]: String(
          updated.sampling_interval_seconds,
        ),
      }));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not update interval.",
      );
    } finally {
      setBusyId(null);
    }
  }

  async function handleTrackingToggle(
    sensor: DeviceDto,
  ) {
    try {
      setBusyId(sensor.id);
      setError("");

      const updated =
        await updateDeviceSampling(
          sensor.id,
          sensor.sampling_interval_seconds,
          !sensor.tracking_enabled,
        );

      setSensors((current) =>
        current.map((item) =>
          item.id === updated.id
            ? updated
            : item,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not update tracking.",
      );
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() =>
            handleAddSensor("moisture")
          }
          className="rounded bg-green-600 px-3 py-2 text-sm text-white hover:bg-green-700"
        >
          Add Moisture
        </button>

        <button
          type="button"
          onClick={() =>
            handleAddSensor("light")
          }
          className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700"
        >
          Add Light
        </button>
      </div>

      <p className="text-xs text-gray-500">
        Latest readings update by temporary polling.
        Phase 12 will replace this with WebSocket updates.
      </p>

      {loading && (
        <p className="text-sm text-gray-500">
          Loading sensors...
        </p>
      )}

      {error && (
        <p className="rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {!loading &&
        sensors.length === 0 &&
        !error && (
          <p className="text-sm text-gray-500">
            No sensors yet.
          </p>
        )}

      <div className="space-y-3">
        {sensors.map((sensor) => {
          const reading =
            latestReadings[sensor.id];

          const busy =
            busyId === sensor.id;

          return (
            <div
              key={sensor.id}
              className="rounded border p-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">
                    {sensor.display_name}
                  </p>

                  <p className="text-sm text-gray-500">
                    {sensor.device_type}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                    {sensor.device_family}
                  </span>

                  <span
                    className={`rounded px-2 py-1 text-xs ${
                      sensor.tracking_enabled
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {sensor.tracking_enabled
                      ? "Tracking ON"
                      : "Tracking OFF"}
                  </span>
                </div>
              </div>

              <div className="mt-4 rounded bg-gray-50 p-3">
                {reading ? (
                  <>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xl font-semibold text-gray-900">
                        {reading.value}{" "}
                        {reading.unit}
                      </span>

                      <span className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700">
                        {reading.source}
                      </span>
                    </div>

                    <p className="mt-1 text-xs text-gray-500">
                      {new Date(
                        reading.recorded_at,
                      ).toLocaleString()}
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">
                    No stored reading yet.
                  </p>
                )}
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    handleReadNow(sensor)
                  }
                  className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {busy
                    ? "Working..."
                    : "Read now"}
                </button>

                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    handleTrackingToggle(
                      sensor,
                    )
                  }
                  className={`rounded px-3 py-2 text-sm text-white disabled:opacity-50 ${
                    sensor.tracking_enabled
                      ? "bg-red-600 hover:bg-red-700"
                      : "bg-green-600 hover:bg-green-700"
                  }`}
                >
                  {sensor.tracking_enabled
                    ? "Stop tracking"
                    : "Start tracking"}
                </button>
              </div>

              <div className="mt-4">
                <label className="mb-1 block text-xs font-medium text-gray-600">
                  Sampling interval (seconds)
                </label>

                <div className="flex gap-2">
                  <input
                    type="number"
                    min="5"
                    step="1"
                    value={
                      intervalValues[
                        sensor.id
                      ] ?? ""
                    }
                    onChange={(event) =>
                      setIntervalValues(
                        (current) => ({
                          ...current,
                          [sensor.id]:
                            event.target.value,
                        }),
                      )
                    }
                    className="w-32 rounded border px-3 py-2 text-sm"
                  />

                  <button
                    type="button"
                    disabled={busy}
                    onClick={() =>
                      handleSaveInterval(
                        sensor,
                      )
                    }
                    className="rounded bg-gray-800 px-3 py-2 text-sm text-white hover:bg-gray-900 disabled:opacity-50"
                  >
                    Save interval
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}