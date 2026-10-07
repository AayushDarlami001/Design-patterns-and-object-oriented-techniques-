import {
  useEffect,
  useState,
} from "react";

import {
  evaluateAutomation,
  getAutomationStrategy,
  getLocations,
  saveAutomationStrategy,
  type AutomationEvaluationDto,
  type LocationListItem,
  type StrategyKey,
} from "../../services/api";

export default function StrategyPanel() {
  const [
    locations,
    setLocations,
  ] = useState<LocationListItem[]>([]);

  const [
    selectedLocationId,
    setSelectedLocationId,
  ] = useState("");

  const [
    strategyKey,
    setStrategyKey,
  ] = useState<StrategyKey>(
    "conservative",
  );

  const [
    result,
    setResult,
  ] =
    useState<AutomationEvaluationDto | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    evaluating,
    setEvaluating,
  ] = useState(false);

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  useEffect(() => {
    async function load() {
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

    load();
  }, []);

  useEffect(() => {
    if (!selectedLocationId) {
      return;
    }

    async function loadStrategy() {
      try {
        setError("");
        setMessage("");
        setResult(null);

        const saved =
          await getAutomationStrategy(
            selectedLocationId,
          );

        setStrategyKey(
          saved.strategy_key,
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load strategy.",
        );
      }
    }

    loadStrategy();
  }, [selectedLocationId]);

  async function handleSave() {
    if (!selectedLocationId) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const saved =
        await saveAutomationStrategy(
          selectedLocationId,
          strategyKey,
        );

      setStrategyKey(
        saved.strategy_key,
      );

      setMessage(
        `Strategy saved: ${saved.strategy_key}`,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not save strategy.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleEvaluate() {
    if (!selectedLocationId) {
      return;
    }

    try {
      setEvaluating(true);
      setError("");
      setMessage("");

      const evaluation =
        await evaluateAutomation(
          selectedLocationId,
        );

      setResult(evaluation);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not evaluate automation.",
      );
    } finally {
      setEvaluating(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-lg border bg-white p-5">
        <p className="text-sm text-gray-500">
          Loading automation...
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-white p-5">
      <div className="mb-5">
        <h2 className="text-lg font-semibold">
          Automation Strategy
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Select how irrigation decisions
          are made from zone moisture
          readings and thresholds.
        </p>
      </div>

      {locations.length === 0 ? (
        <div className="rounded bg-yellow-50 p-3 text-sm text-yellow-800">
          No locations exist yet. Create a
          location in Configuration first.
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium">
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
                      key={
                        location.id
                      }
                      value={
                        location.id
                      }
                    >
                      {location.name}
                    </option>
                  ),
                )}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Strategy
              </label>

              <select
                value={strategyKey}
                onChange={(event) =>
                  setStrategyKey(
                    event.target
                      .value as StrategyKey,
                  )
                }
                className="w-full rounded border px-3 py-2"
              >
                <option value="conservative">
                  Conservative
                </option>

                <option value="aggressive">
                  Aggressive
                </option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={saving}
              onClick={handleSave}
              className="rounded bg-gray-800 px-4 py-2 text-sm text-white hover:bg-gray-900 disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : "Save strategy"}
            </button>

            <button
              type="button"
              disabled={evaluating}
              onClick={
                handleEvaluate
              }
              className="rounded bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
            >
              {evaluating
                ? "Evaluating..."
                : "Evaluate"}
            </button>
          </div>

          {message && (
            <div className="mt-4 rounded bg-green-50 p-3 text-sm text-green-700">
              {message}
            </div>
          )}

          {error && (
            <div className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-4">
              <div className="rounded border bg-gray-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-semibold">
                    Evaluation
                  </h3>

                  <span className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700">
                    {
                      result.strategy_key
                    }
                  </span>
                </div>

                <div className="mt-3">
                  <span
                    className={`inline-block rounded px-3 py-1 text-sm font-medium ${
                      result.action ===
                      "irrigate"
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    {result.action}
                  </span>

                  <p className="mt-2 text-sm text-gray-700">
                    {result.reason}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="mb-2 font-semibold">
                  Zone recommendations
                </h3>

                {result.zones.length ===
                0 ? (
                  <p className="text-sm text-gray-500">
                    No zones available.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {result.zones.map(
                      (zone) => (
                        <div
                          key={
                            zone.zone_id
                          }
                          className="rounded border p-3"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <p className="font-medium">
                              {
                                zone.zone_name
                              }
                            </p>

                            <span
                              className={`rounded px-2 py-1 text-xs ${
                                zone.action ===
                                "irrigate"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-700"
                              }`}
                            >
                              {
                                zone.action
                              }
                            </span>
                          </div>

                          <p className="mt-2 text-sm text-gray-600">
                            {
                              zone.reason
                            }
                          </p>

                          {zone.score !==
                            null && (
                            <p className="mt-1 text-xs text-gray-400">
                              Score:{" "}
                              {
                                zone.score
                              }
                            </p>
                          )}
                        </div>
                      ),
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}