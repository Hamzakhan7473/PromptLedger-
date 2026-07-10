import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { SettingsForm } from "@/components/SettingsForm";

export default function SettingsPage() {
  return (
    <AppShell
      title="Settings"
      description="Organization, model routing, and enterprise options."
    >
      <AuthGuard>
        <SettingsForm />
      </AuthGuard>
    </AppShell>
  );
}
