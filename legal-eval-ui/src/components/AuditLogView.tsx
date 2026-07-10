"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchAuditLog, type AuditEvent } from "@/lib/api";

export function AuditLogView() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditLog()
      .then(setEvents)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return (
      <p className="text-sm text-red-700 border border-red-200 bg-red-50 p-3">
        {error}{" "}
        <Link href="/settings" className="underline">
          Settings
        </Link>
      </p>
    );
  }

  if (events.length === 0) {
    return <p className="text-sm text-neutral-500">No audit events yet.</p>;
  }

  return (
    <ul className="card-surface divide-y divide-border overflow-hidden text-sm">
      {events.map((event) => (
        <li key={event.event_id} className="px-4 py-4 hover:bg-muted/40">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs text-neutral-500">
              {new Date(event.created_at).toLocaleString()}
            </span>
            <span className="font-medium">{event.action}</span>
            {event.resource_id && (
              <span className="font-mono text-xs text-neutral-600">{event.resource_id}</span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
