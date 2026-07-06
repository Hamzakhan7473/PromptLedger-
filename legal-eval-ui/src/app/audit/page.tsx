import { AppShell } from "@/components/AppShell";
import { AuditLogView } from "@/components/AuditLogView";

export default function AuditPage() {
  return (
    <AppShell
      title="Audit log"
      description="Immutable record of uploads, runs, settings changes, and share links."
    >
      <AuditLogView />
    </AppShell>
  );
}
