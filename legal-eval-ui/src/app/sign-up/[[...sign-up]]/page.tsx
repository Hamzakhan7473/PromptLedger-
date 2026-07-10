import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";

export default function SignUpPage() {
  return (
    <div className="public-light-shell min-h-screen flex items-center justify-center px-4 py-12">
      <Suspense fallback={<p className="text-sm text-muted-foreground">Loading…</p>}>
        <AuthForm mode="sign-up" />
      </Suspense>
    </div>
  );
}
