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
  zone_id: string | null;
  location_id: string | null;
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};

export type ReadingDto = {
  device_id: string;
  value: number;
  unit: string;
  source: string;
  recorded_at: string;
};

export type ZoneDto = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};

export type LocationListItem = {
  id: string;
  name: string;
};

export type LocationConfigResponse = {
  location: {
    id: string;
    name: string;
  };
  zones: ZoneDto[];
};

export type ZoneInput = {
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule?: Record<string, unknown>;
};

export type StrategyKey =
  | "conservative"
  | "aggressive";

export type StrategyDto = {
  location_id: string;
  strategy_key: StrategyKey;
};

export type ZoneRecommendationDto = {
  zone_id: string;
  zone_name: string;
  action: string;
  reason: string;
  score: number | null;
};

export type AutomationEvaluationDto = {
  location_id: string;
  strategy_key: StrategyKey;
  action: string;
  reason: string;
  zones: ZoneRecommendationDto[];
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

async function getErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  const data = await response
    .json()
    .catch(() => null);

  return data?.detail || fallback;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch backend health",
    );
  }

  return response.json();
}

export async function getSensors(): Promise<Sensor[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch sensors",
    );
  }

  return response.json();
}

export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<Sensor> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        type,
        display_name: displayName,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      "Failed to create sensor",
    );
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

  const response = await fetch(
    `${API_BASE_URL}/api/devices${
      query ? `?${query}` : ""
    }`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch devices",
    );
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
    throw new Error(
      "Failed to provision device family",
    );
  }

  return response.json();
}

export async function readSensor(
  deviceId: string,
): Promise<ReadingDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/read`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to read sensor",
      ),
    );
  }

  return response.json();
}

export async function getSensorReadings(
  deviceId: string,
  limit = 20,
): Promise<ReadingDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/readings?limit=${limit}`,
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to fetch readings",
      ),
    );
  }

  return response.json();
}

export async function updateDeviceSampling(
  deviceId: string,
  samplingIntervalSeconds: number,
  trackingEnabled: boolean,
): Promise<DeviceDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/sampling`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        sampling_interval_seconds:
          samplingIntervalSeconds,
        tracking_enabled:
          trackingEnabled,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to update sampling",
      ),
    );
  }

  return response.json();
}

export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<DeviceDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to assign device to zone",
      ),
    );
  }

  return response.json();
}

export async function getLocations(): Promise<
  LocationListItem[]
> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch locations",
    );
  }

  return response.json();
}

export async function getLocationConfig(
  locationId: string,
): Promise<LocationConfigResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/config`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch location configuration",
    );
  }

  return response.json();
}

export async function createLocationConfig(
  locationName: string,
  zones: ZoneInput[],
): Promise<LocationConfigResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/config`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        location_name: locationName,
        zones,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to create location",
      ),
    );
  }

  return response.json();
}

export async function deleteLocation(
  locationId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to delete location",
      ),
    );
  }
}

export async function addZone(
  locationId: string,
  zone: ZoneInput,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(zone),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to add zone",
      ),
    );
  }

  return response.json();
}

export async function updateZone(
  locationId: string,
  zoneId: string,
  zone: Partial<ZoneInput>,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(zone),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to update zone",
      ),
    );
  }

  return response.json();
}

export async function deleteZone(
  locationId: string,
  zoneId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to delete zone",
      ),
    );
  }
}

export async function getZoneDevices(
  locationId: string,
  zoneId: string,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}/devices`,
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to fetch zone devices",
      ),
    );
  }

  return response.json();
}

export async function getAutomationStrategy(
  locationId: string,
): Promise<StrategyDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/automation`,
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to load strategy",
      ),
    );
  }

  return response.json();
}

export async function saveAutomationStrategy(
  locationId: string,
  strategyKey: StrategyKey,
): Promise<StrategyDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/automation`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        strategy_key: strategyKey,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to save strategy",
      ),
    );
  }

  return response.json();
}

export async function evaluateAutomation(
  locationId: string,
): Promise<AutomationEvaluationDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/automation/evaluate`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        "Failed to evaluate automation",
      ),
    );
  }

  return response.json();
}