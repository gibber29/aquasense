import AuthShell from "@/components/AuthShell";
import LoginCard from "@/components/LoginCard";

export default function LoginPage() {
  return (
    <AuthShell>
      <LoginCard mode="login" />
    </AuthShell>
  );
}
