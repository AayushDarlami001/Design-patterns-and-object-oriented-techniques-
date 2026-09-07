import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "../services/api";

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getHealth()
      .then((data) => {
        setHealth(data);
        setError(false);
      })
      .catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <span className="rounded-full bg-red-100 px-3 py-1 text-sm text-red-700">
        Backend Offline
      </span>
    );
  }

  if (!health) {
    return (
      <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
        Checking...
      </span>
    );
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-sm font-medium ${
        health.db === "ok"
          ? "bg-green-100 text-green-700"
          : "bg-yellow-100 text-yellow-700"
      }`}
    >
      API: {health.status} | DB: {health.db}
    </span>
  );
}