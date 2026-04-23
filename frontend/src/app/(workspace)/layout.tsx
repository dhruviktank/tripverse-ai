"use client";

import { ReactNode } from "react";
import { WorkspaceShell } from "@/components/workspace-shell";
import AuthGuard from "@/components/auth-guard";
import TripChatbot from "@/components/chatbot";

export default function WorkspaceLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <WorkspaceShell>{children}</WorkspaceShell>
      <TripChatbot />
    </AuthGuard>
  );
}
