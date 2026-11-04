import DeviceList from "../components/devices/DeviceList";
import LocationConfigWizard from "../components/config/LocationConfigWizard";
import OverviewPanel from "../components/overview/OverviewPanel";
import ExecutionLog from "../components/ExecutionLog";
import StrategyPanel from "../features/automation/StrategyPanel";
import SensorList from "../features/sensors/SensorList";

export default function DashboardPage() {
  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-gray-900">
        Greenhouse Dashboard
      </h2>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <section
          id="overview"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2 xl:col-span-3"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Overview
          </h3>

          <OverviewPanel />
        </section>

        <section
          id="sensors"
          className="rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Sensors
          </h3>

          <SensorList />
        </section>

        <section
          id="devices"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Devices
          </h3>

          <DeviceList />
        </section>

        <section
          id="configuration"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2 xl:col-span-3"
        >
          <h3 className="mb-4 text-lg font-semibold text-gray-900">
            Configuration
          </h3>

          <LocationConfigWizard />
        </section>

        <section
          id="automation"
          className="md:col-span-2 xl:col-span-3"
        >
          <StrategyPanel />
        </section>

        <section
          id="controls"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2 xl:col-span-3"
        >
          <ExecutionLog />
        </section>

        <section
          id="events"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2 xl:col-span-3"
        >
          <h3 className="text-lg font-semibold text-gray-900">
            Events
          </h3>

          <p className="mt-2 text-sm text-gray-500">
            Placeholder for events functionality.
          </p>
        </section>
      </div>
    </div>
  );
}