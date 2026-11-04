import { useEffect, useState } from "react";

import type {
  ActuatorExecutionDto,
} from "../services/api";

import {
  getActuatorExecutions,
} from "../services/api";


export default function ExecutionLog() {
  const [
    executions,
    setExecutions,
  ] = useState<ActuatorExecutionDto[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  async function loadExecutions() {
    try {
      setLoading(true);
      setError(null);

      const data =
        await getActuatorExecutions(20);

      setExecutions(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load executions",
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadExecutions();
  }, []);


  if (loading) {
    return (
      <div
        className="
          rounded-lg
          border
          bg-white
          p-4
        "
      >
        Loading execution log...
      </div>
    );
  }


  return (
    <section className="space-y-4">
      <div>
        <h2
          className="
            text-xl
            font-semibold
          "
        >
          Actuator Execution Log
        </h2>

        <p
          className="
            mt-1
            text-sm
            text-gray-500
          "
        >
          Commands normally succeed and are
          recorded with the logging policy.
        </p>

        <p
          className="
            mt-1
            text-sm
            text-gray-500
          "
        >
          If an actuator has been running for
          at least 30 minutes, the max-run-time
          policy blocks the attempt.
        </p>

        <p
          className="
            mt-1
            text-sm
            text-gray-500
          "
        >
          A blocked attempt shows
          &quot;Max run time exceeded&quot; and
          the policies maxRunTime and logging.
        </p>
      </div>


      <button
        type="button"
        onClick={loadExecutions}
        className="
          rounded-md
          bg-slate-900
          px-4
          py-2
          text-sm
          font-medium
          text-white
          hover:bg-slate-700
        "
      >
        Refresh log
      </button>


      {error && (
        <div
          className="
            rounded-md
            border
            border-red-300
            bg-red-50
            p-3
            text-sm
            text-red-700
          "
        >
          {error}
        </div>
      )}


      {executions.length === 0 ? (
        <div
          className="
            rounded-lg
            border
            bg-white
            p-4
            text-sm
            text-gray-500
          "
        >
          No actuator executions yet.
        </div>
      ) : (
        <div className="space-y-3">
          {executions.map(
            (execution) => (
              <div
                key={execution.id}
                className="
                  rounded-lg
                  border
                  bg-white
                  p-4
                  shadow-sm
                "
              >
                <div
                  className="
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-2
                  "
                >
                  <span
                    className={
                      execution.success
                        ? `
                          rounded
                          bg-green-100
                          px-2
                          py-1
                          text-sm
                          font-medium
                          text-green-700
                        `
                        : `
                          rounded
                          bg-red-100
                          px-2
                          py-1
                          text-sm
                          font-medium
                          text-red-700
                        `
                    }
                  >
                    {execution.success
                      ? "SUCCESS"
                      : "FAILED"}
                  </span>

                  <span
                    className="
                      text-xs
                      text-gray-500
                    "
                  >
                    {new Date(
                      execution.created_at,
                    ).toLocaleString()}
                  </span>
                </div>


                <div
                  className="
                    mt-3
                    space-y-2
                    text-sm
                  "
                >
                  <div>
                    <strong>
                      Device:
                    </strong>{" "}
                    {execution.device_id}
                  </div>

                  <div>
                    <strong>
                      Policies:
                    </strong>{" "}

                    {execution.policy_applied
                      .join(", ")}
                  </div>

                  <div>
                    <strong>
                      Message:
                    </strong>{" "}

                    {execution.message ??
                      "None"}
                  </div>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </section>
  );
}