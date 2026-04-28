import AuthShell from "@/components/AuthShell";
import LoginCard from "@/components/LoginCard";

export default function RegisterPage() {
  return (
    <AuthShell>
      <LoginCard mode="register" />
    </AuthShell>
  );
}
