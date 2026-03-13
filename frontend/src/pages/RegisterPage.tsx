import { useState, useRef } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Field, FieldLabel } from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useNavigate, Link } from "react-router-dom";
import * as api from "../api";
import { toast } from "sonner";

const RegisterPage = () => {
  const navigate = useNavigate();
  const emailInput = useRef<HTMLInputElement | null>(null);
  const passwordInput = useRef<HTMLInputElement | null>(null);
  const confirmPasswordInput = useRef<HTMLInputElement | null>(null);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const onRegister = async () => {
    const email = emailInput.current?.value || null;
    const password = passwordInput.current?.value || null;
    const confirmPassword = confirmPasswordInput.current?.value || null;

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    let resp: Response;

    try {
      resp = await api.register({
        email: email,
        password: password,
      });
    }
    catch (error) {
      console.error(error)
      if (error instanceof Error) {
        toast.error(error.message)
      }
      else {
        toast.error('Unexpected error')
      }
      return;
    }

    if (!resp.ok) {
      const data = await resp.json();

      if (resp.status == 422) {
        const message =
          data.detail
            ?.map((item: any) => `(${item.loc.at(-1)}) ${item.msg}`)
            .join("\n") ?? resp.statusText;
        setError(message);
      } else {
        if (data.detail) {
          toast.error(data.detail);
        } else {
          toast.error(resp.statusText);
        }
      }
      return;
    }

    toast.success("Registered");
    navigate("/login");
  };

  return (
    <main className="min-h-screen bg-slate-100 flex items-center justify-center">
      <Card className="w-full max-w-md shadow-xl rounded-2xl">
        <CardContent className="p-8 space-y-3 flex flex-col">
          <h1 className="text-2xl font-bold text-center">Register</h1>

          <Field>
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <Input ref={emailInput} id="email" type="text" />
          </Field>

          <Field>
            <FieldLabel htmlFor="password">Password</FieldLabel>
            <div className="flex">
              <Input
                ref={passwordInput}
                id="password"
                type={showPassword ? "text" : "password"}
              />
              <Button
                className="cursor-pointer"
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </Field>

          <Field>
            <FieldLabel htmlFor="confirm-password">Confirm password</FieldLabel>
            <div className="flex">
              <Input
                ref={confirmPasswordInput}
                id="confirm-password"
                type={showConfirmPassword ? "text" : "password"}
              />
              <Button
                className="cursor-pointer"
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </Field>

          {error && (
            <Alert variant="destructive">
              <AlertDescription className="whitespace-pre-line">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <Button className="cursor-pointer" onClick={onRegister}>
            Register
          </Button>

          <div className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              to="/login"
              className="underline underline-offset-4 hover:text-foreground"
            >
              Login
            </Link>
          </div>
        </CardContent>
      </Card>
    </main>
  );
};

export default RegisterPage;
