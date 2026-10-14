import {
  useEffect,
  useState,
} from "react";

import {
  getLocationOverview,
  getLocations,
  type LocationListItem,
  type LocationOverviewDto,
} from "../../services/api";

export default function OverviewPanel() {
  const [
    locations,
    setLocations,
  ] = useState<LocationListItem[]>([]);

  const [
    selectedLocationId,
    setSelectedLocationId,
  ] = useState("");

  const [
    overview,
    setOverview,
  ] =
    useState<LocationOverviewDto | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  async function loadOverview(
    locationId: string,
    refresh = false,
  ) {
    if (!locationId) {
      return;
    }

    try {
      if (refresh) {
        setRefreshing(true);
      }

      setError("");

      const data =
        await getLocationOverview(
          locationId,
        );

      setOverview(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load overview.",
      );
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    async function loadLocations() {
      try {
        setLoading(true);
        setError("");

        const data =
          await getLocations();

        setLocations(data);

        if (data.length > 0) {
          setSelectedLocationId(
            data[0].id,
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load locations.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadLocations();
  }, []);

  useEffect(() => {
    if (!selectedLocationId) {
      return;
    }

    loadOverview(
      selectedLocationId,
    );
  }, [selectedLocationId]);

  if (loading) {
    return (
      <p className="text-sm text-gray-500">
        Loading overview...
      </p>
    );
  }

  if (locations.length === 0) {
    return (
      <div className="rounded bg-yellow-50 p-3 text-sm text-yellow-800">
        No locations exist yet.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-64 flex-1">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Location
          </label>

          <select
            value={
              selectedLocationId
            }
            onChange={(event) =>
              setSelectedLocationId(
                event.target.value,
              )
            }
            className="w-full rounded border px-3 py-2"
          >
            {locations.map(
              (location) => (
                <option
                  key={location.id}
                  value={location.id}
                >
                  {location.name}
                </option>
              ),
            )}
          </select>
        </div>

        <button
          type="button"
          disabled={refreshing}
          onClick={() =>
            loadOverview(
              selectedLocationId,
              true,
            )
          }
          className="rounded bg-gray-800 px-4 py-2 text-sm text-white hover:bg-gray-900 disabled:opacity-50"
        >
          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {overview && (
        <>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              {
                overview.location
                  .name
              }
            </h3>

            <p className="text-xs text-gray-500">
              Location ID:{" "}
              {
                overview.location
                  .id
              }
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded border bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Assigned sensors
              </p>

              <p className="mt-1 text-2xl font-semibold">
                {
                  overview
                    .device_counts
                    .sensor
                }
              </p>
            </div>

            <div className="rounded border bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Assigned actuators
              </p>

              <p className="mt-1 text-2xl font-semibold">
                {
                  overview
                    .device_counts
                    .actuator
                }
              </p>
            </div>

            <div className="rounded border bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Strategy
              </p>

              <p className="mt-1 font-semibold">
                {overview.strategy_key ??
                  "No strategy saved"}
              </p>
            </div>

            <div className="rounded border bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Recommendation
              </p>

              <p className="mt-1 font-semibold">
                {overview
                  .last_recommendation
                  ?.action ??
                  "Not available"}
              </p>
            </div>
          </div>

          <div className="rounded border bg-white p-4">
            <h4 className="font-semibold text-gray-900">
              Last recommendation
            </h4>

            {overview
              .last_recommendation ? (
              <>
                <span
                  className={`mt-3 inline-block rounded px-3 py-1 text-sm font-medium ${
                    overview
                      .last_recommendation
                      .action ===
                    "irrigate"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {
                    overview
                      .last_recommendation
                      .action
                  }
                </span>

                <p className="mt-2 text-sm text-gray-600">
                  {
                    overview
                      .last_recommendation
                      .reason
                  }
                </p>
              </>
            ) : (
              <p className="mt-2 text-sm text-gray-500">
                No strategy is saved, so
                there is no recommendation.
              </p>
            )}
          </div>

          <div>
            <h4 className="mb-3 text-lg font-semibold text-gray-900">
              Zones
            </h4>

            <div className="space-y-4">
              {overview.zones.map(
                (zone) => (
                  <div
                    key={zone.id}
                    className="rounded border bg-white p-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <h5 className="font-semibold">
                          {zone.name}
                        </h5>

                        <p className="mt-1 text-xs text-gray-500">
                          Moisture thresholds:
                          {" "}
                          {
                            zone
                              .moisture_threshold_low
                          }
                          {" – "}
                          {
                            zone
                              .moisture_threshold_high
                          }
                        </p>
                      </div>

                      <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                        {
                          zone.devices
                            .length
                        }{" "}
                        device(s)
                      </span>
                    </div>

                    {zone.devices
                      .length === 0 ? (
                      <p className="mt-4 rounded bg-gray-50 p-3 text-sm text-gray-500">
                        No devices assigned
                        to this zone.
                      </p>
                    ) : (
                      <div className="mt-4 space-y-3">
                        {zone.devices.map(
                          (device) => {
                            const reading =
                              zone.latest_readings.find(
                                (
                                  item,
                                ) =>
                                  item.device_id ===
                                  device.id,
                              );

                            return (
                              <div
                                key={
                                  device.id
                                }
                                className="rounded border p-3"
                              >
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                  <div>
                                    <p className="font-medium">
                                      {device.display_name ??
                                        device.device_type}
                                    </p>

                                    <p className="text-xs text-gray-500">
                                      {
                                        device.device_type
                                      }
                                      {" · "}
                                      {
                                        device.role
                                      }
                                    </p>
                                  </div>

                                  <span className="rounded bg-blue-50 px-2 py-1 text-xs text-blue-700">
                                    {
                                      device.role
                                    }
                                  </span>
                                </div>

                                {reading ? (
                                  <div className="mt-3 rounded bg-gray-50 p-3">
                                    <p className="text-lg font-semibold">
                                      {
                                        reading.value
                                      }{" "}
                                      {
                                        reading.unit
                                      }
                                    </p>

                                    <p className="mt-1 text-xs text-gray-500">
                                      Tracking:{" "}
                                      {reading.tracking_enabled
                                        ? "ON"
                                        : "OFF"}
                                    </p>

                                    <p className="text-xs text-gray-500">
                                      Sampling interval:{" "}
                                      {
                                        reading.sampling_interval_seconds
                                      }{" "}
                                      seconds
                                    </p>

                                    <p className="text-xs text-gray-400">
                                      Latest reading:{" "}
                                      {new Date(
                                        reading.recorded_at,
                                      ).toLocaleString()}
                                    </p>
                                  </div>
                                ) : (
                                  <p className="mt-3 rounded bg-gray-50 p-3 text-sm text-gray-500">
                                    No reading
                                    available.
                                  </p>
                                )}
                              </div>
                            );
                          },
                        )}
                      </div>
                    )}
                  </div>
                ),
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}