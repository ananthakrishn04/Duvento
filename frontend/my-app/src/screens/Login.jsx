import { EyeIcon } from "lucide-react";
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Checkbox } from "../components/ui/checkbox";
import { Input } from "../components/ui/input";
import { Separator } from "../components/ui/seperator";
import { useAuth } from "../context/AuthContext";

export const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      navigate("/landing");
    }
  };

  // Data for social login buttons
  const socialLogins = [
    {
      name: "GOOGLE",
      color: "#d0021b",
      icon: "https://c.animaapp.com/maihfzolvngpdA/img/clip-path-group.png",
      iconBg: "https://c.animaapp.com/maihfzolvngpdA/img/vector.svg",
    },
    {
      name: "GITHUB",
      color: "#7986cb",
      icon: "https://c.animaapp.com/maihfzolvngpdA/img/5847f98fcef1014c0b5e48c0-1.png",
    },
    {
      name: "LINKEDIN",
      color: "#00bcd4",
      icon: "https://c.animaapp.com/maihfzolvngpdA/img/group.png",
    },
  ];

  return (
    <div className="min-h-screen w-full relative" >
      {/* Background decoration */}
      <div className="fixed inset-0 w-full h-full" >
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

            {/* Social login buttons */}
            <div className="flex gap-4 w-full justify-center">
              {socialLogins.map((social, index) => (
                <Button
                  key={index}
                  type="button"
                  variant="outline"
                  className="w-[130px] h-9 rounded-[18px] border border-solid flex items-center justify-center"
                  style={{ borderColor: social.color, color: social.color }}
                >
                  {social.name === "GOOGLE" ? (
                    <div className="relative w-[27px] h-[27px] mr-2 bg-[url(https://c.animaapp.com/maihfzolvngpdA/img/vector.svg)] bg-[100%_100%]">
                      <div className="relative w-[18px] h-[18px] top-1 left-1 bg-[url(https://c.animaapp.com/maihfzolvngpdA/img/clip-path-group.png)] bg-[100%_100%]" />
                    </div>
                  ) : (
                    <img
                      className="w-5 h-5 mr-2"
                      alt={social.name}
                      src={social.icon}
                    />
                  )}
                  <span className="font-['Open_Sans',Helvetica] font-semibold text-sm text-center">
                    {social.name}
                  </span>
                </Button>
              ))}
            </div>

            {/* Divider */}
            <div className="w-full flex items-center justify-center gap-4">
              <Separator className="w-[100px]" />
              <div className="font-['Open_Sans',Helvetica] font-normal text-[#0000008a] text-sm text-center">
                Or sign in with email
              </div>
              <Separator className="w-[100px]" />
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="w-full space-y-4 px-8">
              {/* Username input */}
              <div className="w-full">
                <Input
                  className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px]"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
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

              {/* Remember me and Forgot password */}
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="remember"
                    className="w-[13px] h-[13px] rounded-sm border border-solid border-[#00000042]"
                  />
                  <label
                    htmlFor="remember"
                    className="font-['Open_Sans',Helvetica] font-normal text-[#000000de] text-[11px]"
                  >
                    Remember
                  </label>
                </div>
                <button
                  type="button"
                  className="font-['Open_Sans',Helvetica] font-normal text-[#000000de] text-[11px] hover:underline"
                >
                  Forgot password
                </button>
              </div>

              {/* Continue button */}
              <Button
                type="submit"
                onClick={handleSubmit}
                className="w-full h-[41px] bg-[#2196f3] hover:bg-[#1976d2]"
              >
                <div className="font-['Open_Sans',Helvetica] font-semibold text-white text-sm text-center">
                  CONTINUE
                </div>
              </Button>

              {/* Register link */}
              <div className="text-center text-sm">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="text-[#2196f3] hover:underline"
                >
                  Register here
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};


