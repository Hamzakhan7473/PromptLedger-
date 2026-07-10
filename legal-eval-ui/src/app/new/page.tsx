import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { NewEvalForm } from "@/components/NewEvalForm";

export default function NewEvalPage() {
  return (
    <AppShell
      title="New eval"
      description="Upload a dataset, pick models, and run the full legal-eval pipeline."
    >
      <AuthGuard>
        <NewEvalForm />
      </AuthGuard>
    </AppShell>
  );
}
