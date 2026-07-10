import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { OnboardingWizard } from "@/components/OnboardingWizard";

export default function OnboardingPage() {
  return (
    <AppShell
      title="Get started"
      description="A quick setup to help you prove your legal AI pipeline."
      backHref="/dashboard"
      backLabel="← Workspace"
    >
      <AuthGuard>
        <OnboardingWizard />
      </AuthGuard>
    </AppShell>
  );
}
