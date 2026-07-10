"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { fetchOnboardingStatus } from "@/lib/api";

export function OnboardingRedirect() {
  const router = useRouter();

  useEffect(() => {
    fetchOnboardingStatus()
      .then((status) => {
        if (!status.completed) router.replace("/onboarding");
      })
      .catch(() => undefined);
  }, [router]);

  return null;
}
