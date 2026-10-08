import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";

export function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await signup(email, password, name);
      navigate("/");
    } catch (err) {
      const status = (err as { response?: { status?: number } }).response?.status;
      setError(
        status === 409
          ? "An account with this email already exists."
          : "Couldn't create your account — password needs at least 8 characters."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="font-display text-3xl italic mb-1">Ledgerly</h1>
        <p className="text-ink-soft text-sm mb-8">Set up your ledger.</p>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="field-label" htmlFor="name">
              Name
            </label>
            <input
              id="name"
              type="text"
              required
              className="field-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              className="field-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              className="field-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="text-xs text-ink-soft/70 mt-1">At least 8 characters.</p>
          </div>
          {error && <p className="field-error">{error}</p>}
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-sm text-ink-soft mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-ink underline underline-offset-2">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
