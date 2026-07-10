import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { HomeRunList } from "@/components/HomeRunList";
import { OnboardingRedirect } from "@/components/OnboardingRedirect";
import { OrgDashboard } from "@/components/OrgDashboard";

export default function DashboardPage() {
  return (
    <AppShell
      title="Workspace"
      description="Your org's eval runs, reproducibility manifests, and shareable trust reports."
      backHref="/"
      backLabel="← Home"
    >
      <OnboardingRedirect />
      <AuthGuard>
        <div className="space-y-8">
          <OrgDashboard />
          <HomeRunList />
        </div>
      </AuthGuard>
    </AppShell>
  );
}
