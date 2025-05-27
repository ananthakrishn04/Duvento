import { EyeIcon } from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { useAuth } from "../context/AuthContext";

export const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      const success = await register(username, email, password);
      if (success) {
        navigate("/landing");
      }
    } catch (err) {
      setError(err.message || "Registration failed");
    }
  };

  return (
    <div className="min-h-screen w-full relative">
      {/* Background decoration */}
      <div className="fixed inset-0 w-full h-full">
        <img
          className="w-full h-full object-cover"
          alt="Decoration line wing"
          src="https://c.animaapp.com/maihfzolvngpdA/img/decoration---line---wing-mask.png"
        />
      </div>

      {/* Main content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen">
        <Card className="w-[500px] py-8 rounded-[20px] border-none bg-white text-card-foreground">
          <CardContent className="flex flex-col items-center space-y-6">
            {/* Logo */}
            <img
              className="w-[250px]"
              alt="Untitled"
              src="https://c.animaapp.com/maihfzolvngpdA/img/untitled-1.png"
            />

            <div className="font-['Open_Sans',Helvetica] font-bold text-[#c5051d] text-[13px] text-center">
              Where Coders Clash &amp; Legends Rise
            </div>

            {/* Registration Form */}
            <form onSubmit={handleSubmit} className="w-full space-y-4 px-8">
              {/* Username input */}
              <div className="w-full">
                <Input
                  className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px]"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              {/* Email input */}
              <div className="w-full">
                <Input
                  type="email"
                  className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px]"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              {/* Password input */}
              <div className="w-full">
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px] pr-10"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                  >
                    <EyeIcon className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Confirm Password input */}
              <div className="w-full">
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px] pr-10"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Error message */}
              {error && (
                <div className="text-red-500 text-sm text-center">{error}</div>
              )}

              {/* Register button */}
              <Button
                type="submit"
                className="w-full h-[41px] bg-[#2196f3] hover:bg-[#1976d2]"
              >
                <div className="font-['Open_Sans',Helvetica] font-semibold text-white text-sm text-center">
                  REGISTER
                </div>
              </Button>

              {/* Login link */}
              <div className="text-center text-sm">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => navigate("/login")}
                  className="text-[#2196f3] hover:underline"
                >
                  Login here
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}; 