import {
  useEffect,
  useState,
} from "react";

import type {
  CommandLogDto,
  DeviceDto,
} from "../../services/api";

import {
  executeCommand,
  getCommandHistory,
  getDevices,
} from "../../services/api";


export default function CommandPanel() {
  const [actuators, setActuators] =
    useState<DeviceDto[]>([]);

  const [history, setHistory] =
    useState<CommandLogDto[]>([]);

  const [lightLevels, setLightLevels] =
    useState<Record<string, number>>({});

  const [loading, setLoading] =
    useState(true);

  const [busyKey, setBusyKey] =
    useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);


  async function loadData() {
    try {
      setLoading(true);
      setError(null);

      const [
        actuatorData,
        historyData,
      ] = await Promise.all([
        getDevices(
          undefined,
          "actuator",
        ),
        getCommandHistory(50),
      ]);

      setActuators(
        actuatorData,
      );

      setHistory(
        historyData,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load command data",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  async function runCommand(
    device: DeviceDto,
    commandType: string,
  ) {
    const key =
      `${device.id}-${commandType}`;

    try {
      setBusyKey(key);
      setError(null);

      const payload =
        commandType ===
        "set_light_level"
          ? {
              level:
                lightLevels[
                  device.id
                ] ?? 1,
            }
          : {};

      const result =
        await executeCommand(
          commandType,
          device.id,
          payload,
        );

      if (
        result.status === "failed" ||
        result.status === "rejected"
      ) {
        setError(
          result.error_message ??
            `Command ${result.status}`,
        );
      }

      // Reload states and command history
      // after every command attempt.
      const [
        updatedActuators,
        updatedHistory,
      ] = await Promise.all([
        getDevices(
          undefined,
          "actuator",
        ),
        getCommandHistory(50),
      ]);

      setActuators(
        updatedActuators,
      );

      setHistory(
        updatedHistory,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Command failed",
      );
    } finally {
      setBusyKey(null);
    }
  }


  if (loading) {
    return (
      <div className="text-sm text-gray-500">
        Loading actuator controls...
      </div>
    );
  }


  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">
          Actuator Controls
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Commands are enabled only when
          allowed by the actuator state.
        </p>
      </div>


      {error && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}


      {actuators.length === 0 ? (
        <div className="rounded-lg border p-4 text-sm text-gray-500">
          No actuators found.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {actuators.map(
            (device) => {
              const canStart =
                device.allowed_commands.includes(
                  "start_pump",
                );

              const canStop =
                device.allowed_commands.includes(
                  "stop_pump",
                );

              const canSetLight =
                device.allowed_commands.includes(
                  "set_light_level",
                );

              return (
                <div
                  key={device.id}
                  className="rounded-xl border bg-slate-50 p-4"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">
                        {device.display_name}
                      </h4>

                      <p className="text-xs text-gray-500">
                        {device.device_type}
                      </p>
                    </div>

                    <span className="rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold uppercase text-slate-700">
                      {device.state ??
                        "unknown"}
                    </span>
                  </div>


                  <div className="mt-3 text-xs text-gray-500">
                    Allowed:{" "}
                    {device
                      .allowed_commands
                      .join(", ") ||
                      "none"}
                  </div>


                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="button"
                      disabled={
                        !canStart ||
                        busyKey !== null
                      }
                      onClick={() =>
                        runCommand(
                          device,
                          "start_pump",
                        )
                      }
                      className="rounded-md bg-green-600 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      Start Pump
                    </button>


                    <button
                      type="button"
                      disabled={
                        !canStop ||
                        busyKey !== null
                      }
                      onClick={() =>
                        runCommand(
                          device,
                          "stop_pump",
                        )
                      }
                      className="rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      Stop Pump
                    </button>
                  </div>


                  <div className="mt-4 flex flex-wrap items-end gap-2">
                    <label className="text-sm text-gray-700">
                      Light level

                      <input
                        type="number"
                        min="0"
                        step="1"
                        value={
                          lightLevels[
                            device.id
                          ] ?? 1
                        }
                        onChange={(
                          event,
                        ) =>
                          setLightLevels(
                            (
                              current,
                            ) => ({
                              ...current,
                              [
                                device.id
                              ]:
                                Number(
                                  event
                                    .target
                                    .value,
                                ),
                            }),
                          )
                        }
                        className="mt-1 block w-24 rounded-md border px-3 py-2"
                      />
                    </label>


                    <button
                      type="button"
                      disabled={
                        !canSetLight ||
                        busyKey !== null
                      }
                      onClick={() =>
                        runCommand(
                          device,
                          "set_light_level",
                        )
                      }
                      className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      Set Light Level
                    </button>
                  </div>
                </div>
              );
            },
          )}
        </div>
      )}


      <div>
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Command History
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Latest command attempts from
              command_log.
            </p>
          </div>

          <button
            type="button"
            onClick={loadData}
            className="rounded-md border px-3 py-2 text-sm hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>


        {history.length === 0 ? (
          <p className="mt-3 text-sm text-gray-500">
            No commands recorded yet.
          </p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left">
                    Command
                  </th>

                  <th className="px-3 py-2 text-left">
                    Device
                  </th>

                  <th className="px-3 py-2 text-left">
                    Status
                  </th>

                  <th className="px-3 py-2 text-left">
                    Message
                  </th>

                  <th className="px-3 py-2 text-left">
                    Time
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">
                {history.map(
                  (item) => (
                    <tr
                      key={item.id}
                    >
                      <td className="px-3 py-2 font-medium">
                        {
                          item.command_type
                        }
                      </td>

                      <td className="px-3 py-2 font-mono text-xs">
                        {item.device_id}
                      </td>

                      <td className="px-3 py-2">
                        <span
                          className={
                            item.status ===
                            "success"
                              ? "rounded bg-green-100 px-2 py-1 text-xs font-semibold text-green-700"
                              : item.status ===
                                "rejected"
                              ? "rounded bg-yellow-100 px-2 py-1 text-xs font-semibold text-yellow-700"
                              : "rounded bg-red-100 px-2 py-1 text-xs font-semibold text-red-700"
                          }
                        >
                          {item.status}
                        </span>
                      </td>

                      <td className="px-3 py-2 text-gray-600">
                        {item.error_message ??
                          "—"}
                      </td>

                      <td className="px-3 py-2 text-gray-500">
                        {new Date(
                          item.created_at,
                        ).toLocaleString()}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}