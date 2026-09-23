export type HealthResponse = {
  status: string;
  db: "ok" | "fail";
};

export type Sensor = {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
};

export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";


export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("Failed to fetch backend health");
  }

  return response.json();
}


export async function getSensors(): Promise<Sensor[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to fetch sensors");
  }

  return response.json();
}


export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<Sensor> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create sensor");
  }

  return response.json();
}


export async function getDevices(
  family?: string,
  role?: string,
): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.set("family", family);
  }

  if (role) {
    params.set("role", role);
  }

  const query = params.toString();

  const url = `${API_BASE_URL}/api/devices${
    query ? `?${query}` : ""
  }`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch devices");
  }

  return response.json();
}


export async function provisionDeviceFamily(
  family: "simulation" | "edge",
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${family}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to provision device family");
  }

  return response.json();
}