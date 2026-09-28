import { useEffect, useState } from "react";

import {
  addZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  getLocationConfig,
  getLocations,
  getZoneDevices,
  updateZone,
  type DeviceDto,
  type LocationConfigResponse,
  type LocationListItem,
  type ZoneDto,
} from "../../services/api";

type DraftZone = {
  name: string;
  low: string;
  high: string;
  start: string;
  end: string;
};

const emptyZone: DraftZone = {
  name: "",
  low: "0.30",
  high: "0.70",
  start: "",
  end: "",
};

export default function LocationConfigWizard() {
  const [locations, setLocations] = useState<LocationListItem[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [config, setConfig] = useState<LocationConfigResponse | null>(null);

  const [locationName, setLocationName] = useState("");
  const [draftZones, setDraftZones] = useState<DraftZone[]>([
    { ...emptyZone },
  ]);

  const [newZone, setNewZone] = useState<DraftZone>({
    ...emptyZone,
  });

  const [editingZoneId, setEditingZoneId] = useState<string | null>(null);
  const [editingZone, setEditingZone] = useState<DraftZone>({
    ...emptyZone,
  });

  const [zoneDevices, setZoneDevices] = useState<
    Record<string, DeviceDto[]>
  >({});

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadLocations() {
    try {
      setLoading(true);
      setError("");

      const data = await getLocations();
      setLocations(data);
    } catch {
      setError("Could not load locations.");
    } finally {
      setLoading(false);
    }
  }

  async function loadConfig(locationId: string) {
    if (!locationId) {
      setConfig(null);
      setZoneDevices({});
      return;
    }

    try {
      setError("");

      const data = await getLocationConfig(locationId);
      setConfig(data);

      const deviceEntries = await Promise.all(
        data.zones.map(async (zone) => {
          try {
            const devices = await getZoneDevices(
              locationId,
              zone.id,
            );

            return [zone.id, devices] as const;
          } catch {
            return [zone.id, []] as const;
          }
        }),
      );

      setZoneDevices(
        Object.fromEntries(deviceEntries),
      );
    } catch {
      setError("Could not load location configuration.");
    }
  }

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    if (selectedLocationId) {
      loadConfig(selectedLocationId);
    } else {
      setConfig(null);
      setZoneDevices({});
    }
  }, [selectedLocationId]);

  function validateZone(zone: DraftZone): string | null {
    if (!zone.name.trim()) {
      return "Zone name is required.";
    }

    const low = Number(zone.low);
    const high = Number(zone.high);

    if (
      Number.isNaN(low) ||
      Number.isNaN(high)
    ) {
      return "Thresholds must be numbers.";
    }

    if (
      low < 0 ||
      low > 1 ||
      high < 0 ||
      high > 1
    ) {
      return "Thresholds must be between 0 and 1.";
    }

    if (low >= high) {
      return "Low threshold must be less than high threshold.";
    }

    return null;
  }

  function zoneSchedule(zone: DraftZone) {
    const schedule: Record<string, unknown> = {};

    if (zone.start) {
      schedule.start = zone.start;
    }

    if (zone.end) {
      schedule.end = zone.end;
    }

    return schedule;
  }

  function updateDraftZone(
    index: number,
    field: keyof DraftZone,
    value: string,
  ) {
    setDraftZones((current) =>
      current.map((zone, zoneIndex) =>
        zoneIndex === index
          ? {
              ...zone,
              [field]: value,
            }
          : zone,
      ),
    );
  }

  function addDraftZone() {
    setDraftZones((current) => [
      ...current,
      { ...emptyZone },
    ]);
  }

  function removeDraftZone(index: number) {
    setDraftZones((current) => {
      if (current.length === 1) {
        return current;
      }

      return current.filter(
        (_, zoneIndex) => zoneIndex !== index,
      );
    });
  }

  async function handleCreateLocation() {
    setError("");
    setSuccess("");

    if (!locationName.trim()) {
      setError("Location name is required.");
      return;
    }

    const names = new Set<string>();

    for (const zone of draftZones) {
      const validationError = validateZone(zone);

      if (validationError) {
        setError(validationError);
        return;
      }

      const normalized = zone.name.trim().toLowerCase();

      if (names.has(normalized)) {
        setError(
          "Zone names must be unique inside the location.",
        );
        return;
      }

      names.add(normalized);
    }

    try {
      setSaving(true);

      const created = await createLocationConfig(
        locationName.trim(),
        draftZones.map((zone) => ({
          name: zone.name.trim(),
          moisture_threshold_low: Number(zone.low),
          moisture_threshold_high: Number(zone.high),
          schedule: zoneSchedule(zone),
        })),
      );

      await loadLocations();

      setLocationName("");
      setDraftZones([{ ...emptyZone }]);
      setSelectedLocationId(created.location.id);
      setConfig(created);
      setSuccess("Location created successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create location.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteLocation() {
    if (!selectedLocationId) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this location and its zones?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await deleteLocation(selectedLocationId);

      setSelectedLocationId("");
      setConfig(null);
      setZoneDevices({});

      await loadLocations();

      setSuccess("Location deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not delete location.",
      );
    }
  }

  async function handleAddZone() {
    if (!selectedLocationId) {
      return;
    }

    const validationError = validateZone(newZone);

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      await addZone(
        selectedLocationId,
        {
          name: newZone.name.trim(),
          moisture_threshold_low: Number(
            newZone.low,
          ),
          moisture_threshold_high: Number(
            newZone.high,
          ),
          schedule: zoneSchedule(newZone),
        },
      );

      setNewZone({ ...emptyZone });

      await loadConfig(selectedLocationId);

      setSuccess("Zone added successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not add zone.",
      );
    } finally {
      setSaving(false);
    }
  }

  function startEditing(zone: ZoneDto) {
    const schedule = zone.schedule as {
      start?: string;
      end?: string;
    };

    setEditingZoneId(zone.id);

    setEditingZone({
      name: zone.name,
      low: String(zone.moisture_threshold_low),
      high: String(zone.moisture_threshold_high),
      start: schedule.start ?? "",
      end: schedule.end ?? "",
    });
  }

  async function handleUpdateZone() {
    if (
      !selectedLocationId ||
      !editingZoneId
    ) {
      return;
    }

    const validationError =
      validateZone(editingZone);

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      await updateZone(
        selectedLocationId,
        editingZoneId,
        {
          name: editingZone.name.trim(),
          moisture_threshold_low: Number(
            editingZone.low,
          ),
          moisture_threshold_high: Number(
            editingZone.high,
          ),
          schedule: zoneSchedule(editingZone),
        },
      );

      setEditingZoneId(null);

      await loadConfig(selectedLocationId);

      setSuccess("Zone updated successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not update zone.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteZone(
    zoneId: string,
  ) {
    if (!selectedLocationId) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this zone?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await deleteZone(
        selectedLocationId,
        zoneId,
      );

      await loadConfig(selectedLocationId);

      setSuccess("Zone deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not delete zone.",
      );
    }
  }

  return (
    <div className="space-y-6">
      {loading && (
        <p className="text-sm text-gray-500">
          Loading locations...
        </p>
      )}

      {error && (
        <div className="rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      )}

      <div className="rounded-lg border p-4">
        <h4 className="mb-3 font-semibold text-gray-900">
          Saved Locations
        </h4>

        <select
          value={selectedLocationId}
          onChange={(event) =>
            setSelectedLocationId(
              event.target.value,
            )
          }
          className="w-full rounded border px-3 py-2"
        >
          <option value="">
            Select a location
          </option>

          {locations.map((location) => (
            <option
              key={location.id}
              value={location.id}
            >
              {location.name}
            </option>
          ))}
        </select>

        {selectedLocationId && (
          <button
            type="button"
            onClick={handleDeleteLocation}
            className="mt-3 rounded bg-red-600 px-3 py-2 text-sm text-white hover:bg-red-700"
          >
            Delete Location
          </button>
        )}
      </div>

      <div className="rounded-lg border p-4">
        <h4 className="mb-4 font-semibold text-gray-900">
          Create New Location
        </h4>

        <input
          type="text"
          value={locationName}
          onChange={(event) =>
            setLocationName(
              event.target.value,
            )
          }
          placeholder="Location name"
          className="mb-4 w-full rounded border px-3 py-2"
        />

        <div className="space-y-4">
          {draftZones.map((zone, index) => (
            <div
              key={index}
              className="rounded border bg-gray-50 p-3"
            >
              <div className="mb-3 flex items-center justify-between">
                <p className="font-medium">
                  Zone {index + 1}
                </p>

                {draftZones.length > 1 && (
                  <button
                    type="button"
                    onClick={() =>
                      removeDraftZone(index)
                    }
                    className="text-sm text-red-600"
                  >
                    Remove
                  </button>
                )}
              </div>

              <input
                value={zone.name}
                onChange={(event) =>
                  updateDraftZone(
                    index,
                    "name",
                    event.target.value,
                  )
                }
                placeholder="Zone name"
                className="mb-2 w-full rounded border px-3 py-2"
              />

              <div className="grid gap-2 md:grid-cols-2">
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={zone.low}
                  onChange={(event) =>
                    updateDraftZone(
                      index,
                      "low",
                      event.target.value,
                    )
                  }
                  placeholder="Low threshold"
                  className="rounded border px-3 py-2"
                />

                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={zone.high}
                  onChange={(event) =>
                    updateDraftZone(
                      index,
                      "high",
                      event.target.value,
                    )
                  }
                  placeholder="High threshold"
                  className="rounded border px-3 py-2"
                />

                <input
                  type="time"
                  value={zone.start}
                  onChange={(event) =>
                    updateDraftZone(
                      index,
                      "start",
                      event.target.value,
                    )
                  }
                  className="rounded border px-3 py-2"
                />

                <input
                  type="time"
                  value={zone.end}
                  onChange={(event) =>
                    updateDraftZone(
                      index,
                      "end",
                      event.target.value,
                    )
                  }
                  className="rounded border px-3 py-2"
                />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={addDraftZone}
            className="rounded bg-gray-200 px-3 py-2 text-sm"
          >
            Add Another Zone
          </button>

          <button
            type="button"
            onClick={handleCreateLocation}
            disabled={saving}
            className="rounded bg-green-600 px-3 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
          >
            {saving
              ? "Saving..."
              : "Create Location"}
          </button>
        </div>
      </div>

      {config && (
        <div className="rounded-lg border p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h4 className="font-semibold text-gray-900">
                {config.location.name}
              </h4>

              <p className="text-xs text-gray-500">
                {config.location.id}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {config.zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded border p-3"
              >
                {editingZoneId === zone.id ? (
                  <div className="space-y-2">
                    <input
                      value={editingZone.name}
                      onChange={(event) =>
                        setEditingZone({
                          ...editingZone,
                          name: event.target.value,
                        })
                      }
                      className="w-full rounded border px-3 py-2"
                    />

                    <div className="grid gap-2 md:grid-cols-2">
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={editingZone.low}
                        onChange={(event) =>
                          setEditingZone({
                            ...editingZone,
                            low: event.target.value,
                          })
                        }
                        className="rounded border px-3 py-2"
                      />

                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={editingZone.high}
                        onChange={(event) =>
                          setEditingZone({
                            ...editingZone,
                            high: event.target.value,
                          })
                        }
                        className="rounded border px-3 py-2"
                      />

                      <input
                        type="time"
                        value={editingZone.start}
                        onChange={(event) =>
                          setEditingZone({
                            ...editingZone,
                            start: event.target.value,
                          })
                        }
                        className="rounded border px-3 py-2"
                      />

                      <input
                        type="time"
                        value={editingZone.end}
                        onChange={(event) =>
                          setEditingZone({
                            ...editingZone,
                            end: event.target.value,
                          })
                        }
                        className="rounded border px-3 py-2"
                      />
                    </div>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleUpdateZone}
                        className="rounded bg-blue-600 px-3 py-2 text-sm text-white"
                      >
                        Save
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          setEditingZoneId(null)
                        }
                        className="rounded bg-gray-200 px-3 py-2 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-medium">
                          {zone.name}
                        </p>

                        <p className="text-sm text-gray-500">
                          Moisture:{" "}
                          {zone.moisture_threshold_low} –{" "}
                          {zone.moisture_threshold_high}
                        </p>

                        <p className="text-xs text-gray-400">
                          Zone ID: {zone.id}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            startEditing(zone)
                          }
                          className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            handleDeleteZone(
                              zone.id,
                            )
                          }
                          className="rounded bg-red-100 px-2 py-1 text-xs text-red-700"
                        >
                          Delete
                        </button>
                      </div>
                    </div>

                    <div className="mt-3">
                      <p className="text-xs font-medium text-gray-600">
                        Devices
                      </p>

                      {(zoneDevices[zone.id] ?? [])
                        .length === 0 ? (
                        <p className="text-xs text-gray-400">
                          No devices assigned.
                        </p>
                      ) : (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {zoneDevices[
                            zone.id
                          ].map((device) => (
                            <span
                              key={device.id}
                              className="rounded bg-gray-100 px-2 py-1 text-xs"
                            >
                              {device.display_name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>

          <div className="mt-5 rounded border bg-gray-50 p-3">
            <p className="mb-3 font-medium">
              Add Zone
            </p>

            <input
              value={newZone.name}
              onChange={(event) =>
                setNewZone({
                  ...newZone,
                  name: event.target.value,
                })
              }
              placeholder="Zone name"
              className="mb-2 w-full rounded border px-3 py-2"
            />

            <div className="grid gap-2 md:grid-cols-2">
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={newZone.low}
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    low: event.target.value,
                  })
                }
                className="rounded border px-3 py-2"
              />

              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={newZone.high}
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    high: event.target.value,
                  })
                }
                className="rounded border px-3 py-2"
              />

              <input
                type="time"
                value={newZone.start}
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    start: event.target.value,
                  })
                }
                className="rounded border px-3 py-2"
              />

              <input
                type="time"
                value={newZone.end}
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    end: event.target.value,
                  })
                }
                className="rounded border px-3 py-2"
              />
            </div>

            <button
              type="button"
              onClick={handleAddZone}
              disabled={saving}
              className="mt-3 rounded bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50"
            >
              Add Zone
            </button>
          </div>
        </div>
      )}
    </div>
  );
}