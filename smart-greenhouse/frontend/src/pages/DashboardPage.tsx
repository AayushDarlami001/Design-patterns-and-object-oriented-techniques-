import SensorList from "../features/sensors/SensorList";
import DeviceList from "../components/devices/DeviceList";

const sections = [
  { id: "configuration", title: "Configuration" },
  { id: "automation", title: "Automation" },
  { id: "controls", title: "Controls" },
  { id: "events", title: "Events" },
];

export default function DashboardPage() {
  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-gray-900">
        Greenhouse Dashboard
      </h2>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {/* Overview */}
        <section
          id="overview"
          className="rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-gray-900">
            Overview
          </h3>

          <p className="mt-2 text-sm text-gray-500">
            Placeholder for overview functionality.
          </p>
        </section>

        {/* Phase 2 - Sensors */}
        <section
          id="sensors"
          className="rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Sensors
          </h3>

          <SensorList />
        </section>

        {/* Phase 3 - Devices */}
        <section
          id="devices"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Devices
          </h3>

          <DeviceList />
        </section>

        {/* Future sections */}
        {sections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="rounded-xl border bg-white p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-gray-900">
              {section.title}
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Placeholder for {section.title.toLowerCase()} functionality.
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}