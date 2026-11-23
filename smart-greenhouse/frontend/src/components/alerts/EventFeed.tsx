import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getAlerts,
  getLocationConfig,
  getLocations,
  type AlertDto,
  type LocationListItem,
  type ZoneDto,
} from "../../services/api";


export default function EventFeed() {
  const [alerts, setAlerts] =
    useState<AlertDto[]>([]);

  const [locations, setLocations] =
    useState<LocationListItem[]>([]);

  const [zones, setZones] =
    useState<ZoneDto[]>([]);

  const [locationId, setLocationId] =
    useState("");

  const [zoneId, setZoneId] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  async function loadAlerts() {
    try {
      setError("");

      const data = await getAlerts({
        status: "active",
        locationId:
          locationId || undefined,
        zoneId:
          zoneId || undefined,
        limit: 50,
      });

      setAlerts(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load alerts.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function loadLocations() {
    try {
      const data =
        await getLocations();

      setLocations(data);
    } catch {
      setLocations([]);
    }
  }


  useEffect(() => {
    loadLocations();
  }, []);


  useEffect(() => {
    async function loadZones() {
      if (!locationId) {
        setZones([]);
        setZoneId("");
        return;
      }

      try {
        const config =
          await getLocationConfig(
            locationId,
          );

        setZones(config.zones);

        if (
          zoneId &&
          !config.zones.some(
            (zone) =>
              zone.id === zoneId,
          )
        ) {
          setZoneId("");
        }
      } catch {
        setZones([]);
        setZoneId("");
      }
    }

    loadZones();
  }, [locationId]);


  useEffect(() => {
    setLoading(true);

    loadAlerts();

    const interval =
      window.setInterval(
        loadAlerts,
        5000,
      );

    return () => {
      window.clearInterval(
        interval,
      );
    };
  }, [locationId, zoneId]);


  const locationNames =
    useMemo(() => {
      return new Map(
        locations.map(
          (location) => [
            location.id,
            location.name,
          ],
        ),
      );
    }, [locations]);


  const zoneNames =
    useMemo(() => {
      return new Map(
        zones.map(
          (zone) => [
            zone.id,
            zone.name,
          ],
        ),
      );
    }, [zones]);


  function severityClasses(
    severity: AlertDto["severity"],
  ) {
    if (severity === "critical") {
      return (
        "border-red-200 " +
        "bg-red-50 " +
        "text-red-800"
      );
    }

    if (severity === "warning") {
      return (
        "border-amber-200 " +
        "bg-amber-50 " +
        "text-amber-800"
      );
    }

    return (
      "border-sky-200 " +
      "bg-sky-50 " +
      "text-sky-800"
    );
  }


  function severityBadgeClasses(
    severity: AlertDto["severity"],
  ) {
    if (severity === "critical") {
      return (
        "bg-red-100 " +
        "text-red-700"
      );
    }

    if (severity === "warning") {
      return (
        "bg-amber-100 " +
        "text-amber-700"
      );
    }

    return (
      "bg-sky-100 " +
      "text-sky-700"
    );
  }


  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Event Feed
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Active alerts are refreshed
          automatically every 5 seconds.
        </p>
      </div>


      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label
            htmlFor="event-location"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Location
          </label>

          <select
            id="event-location"
            value={locationId}
            onChange={(event) => {
              setLocationId(
                event.target.value,
              );
              setZoneId("");
            }}
            className="
              w-full rounded-lg
              border border-slate-300
              bg-white px-3 py-2
              text-sm text-slate-900
              outline-none
              focus:border-emerald-500
              focus:ring-2
              focus:ring-emerald-100
            "
          >
            <option value="">
              All locations
            </option>

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


        <div>
          <label
            htmlFor="event-zone"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Zone
          </label>

          <select
            id="event-zone"
            value={zoneId}
            onChange={(event) =>
              setZoneId(
                event.target.value,
              )
            }
            disabled={!locationId}
            className="
              w-full rounded-lg
              border border-slate-300
              bg-white px-3 py-2
              text-sm text-slate-900
              outline-none
              disabled:cursor-not-allowed
              disabled:bg-slate-100
              disabled:text-slate-400
              focus:border-emerald-500
              focus:ring-2
              focus:ring-emerald-100
            "
          >
            <option value="">
              All zones
            </option>

            {zones.map(
              (zone) => (
                <option
                  key={zone.id}
                  value={zone.id}
                >
                  {zone.name}
                </option>
              ),
            )}
          </select>
        </div>
      </div>


      {error && (
        <div
          className="
            rounded-lg border
            border-red-200
            bg-red-50
            px-4 py-3
            text-sm text-red-700
          "
        >
          {error}
        </div>
      )}


      {loading ? (
        <div
          className="
            rounded-xl border
            border-slate-200
            bg-white p-6
            text-sm text-slate-500
          "
        >
          Loading alerts...
        </div>
      ) : alerts.length === 0 ? (
        <div
          className="
            rounded-xl border
            border-dashed
            border-slate-300
            bg-slate-50 p-8
            text-center
          "
        >
          <p className="font-medium text-slate-700">
            No active alerts
          </p>

          <p className="mt-1 text-sm text-slate-500">
            New alerts will appear
            here automatically.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map(
            (alert) => (
              <article
                key={alert.id}
                className={`
                  rounded-xl border
                  p-4
                  ${severityClasses(
                    alert.severity,
                  )}
                `}
              >
                <div
                  className="
                    flex flex-col
                    gap-3
                    sm:flex-row
                    sm:items-start
                    sm:justify-between
                  "
                >
                  <div>
                    <div
                      className="
                        flex flex-wrap
                        items-center gap-2
                      "
                    >
                      <span
                        className={`
                          rounded-full
                          px-2.5 py-1
                          text-xs font-semibold
                          uppercase
                          ${severityBadgeClasses(
                            alert.severity,
                          )}
                        `}
                      >
                        {alert.severity}
                      </span>

                      <span
                        className="
                          text-xs font-medium
                          text-slate-500
                        "
                      >
                        {alert.event_type}
                      </span>
                    </div>

                    <p
                      className="
                        mt-3 font-semibold
                        text-slate-900
                      "
                    >
                      {alert.message}
                    </p>

                    <div
                      className="
                        mt-2 space-y-1
                        text-xs text-slate-600
                      "
                    >
                      <p>
                        Device:{" "}
                        {alert.device_id ??
                          "Unassigned"}
                      </p>

                      <p>
                        Location:{" "}
                        {alert.location_id
                          ? locationNames.get(
                              alert.location_id,
                            ) ??
                            alert.location_id
                          : "Unassigned"}
                      </p>

                      <p>
                        Zone:{" "}
                        {alert.zone_id
                          ? zoneNames.get(
                              alert.zone_id,
                            ) ??
                            alert.zone_id
                          : "Unassigned"}
                      </p>
                    </div>
                  </div>

                  <time
                    className="
                      text-xs text-slate-500
                      sm:text-right
                    "
                    dateTime={
                      alert.created_at
                    }
                  >
                    {new Date(
                      alert.created_at,
                    ).toLocaleString()}
                  </time>
                </div>
              </article>
            ),
          )}
        </div>
      )}
    </div>
  );
}