import { AppShell } from "@/components/AppShell";
import { HomeRunList } from "@/components/HomeRunList";
import { OrgDashboard } from "@/components/OrgDashboard";

export default function DashboardPage() {
  return (
    <AppShell
      title="Workspace"
      description="Your org's eval runs, reproducibility manifests, and shareable trust reports."
      backHref="/"
      backLabel="← Home"
    >
      <div className="space-y-8">
        <OrgDashboard />
        <HomeRunList />
      </div>
    </AppShell>
  );
}
