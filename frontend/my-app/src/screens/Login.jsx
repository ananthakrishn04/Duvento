import { EyeIcon } from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
    <div className="bg-neutral-50 flex flex-row justify-center w-full">
      <div className="bg-neutral-50 overflow-hidden w-[1440px] h-[1024px]">
        <div className="relative h-[1028px] top-px">
          {/* Background decoration */}
          <div className="absolute w-[1440px] h-[1028px] top-0 left-0">
            <div className="relative w-[1442px] h-[1030px] -top-px -left-px">
              <img
                className="absolute w-full h-full"
                alt="Decoration line wing"
                src="https://c.animaapp.com/maihfzolvngpdA/img/decoration---line---wing-mask.png"
              />
            </div>
          </div>

          {/* Main login card */}
          <Card className="absolute w-[769px] h-[739px] top-[135px] left-[336px] rounded-[20px] border-none">
            <CardContent className="p-0 h-full">
              <form onSubmit={handleSubmit} className="relative h-[739px]">
                <div className="absolute w-[768px] h-[739px] top-0 left-px">
                  <div className="h-[739px]">
                    <div className="relative w-[770px] h-[741px] -top-px -left-px bg-white rounded-[20px]" />
                  </div>
                </div>

                <img
                  className="absolute w-[769px] h-[739px] top-0 left-0"
                  alt="Line wing mask"
                  src="https://c.animaapp.com/maihfzolvngpdA/img/line---wing-mask.png"
                />

                <div className="absolute top-[165px] left-[272px] font-['Open_Sans',Helvetica] font-bold text-[#c5051d] text-[13px] text-center tracking-[0] leading-[normal]">
                  Where Coders Clash &amp; Legends Rise
                </div>

                {/* Logo */}
                <img
                  className="absolute w-[347px] h-[97px] top-[70px] left-[220px]"
                  alt="Untitled"
                  src="https://c.animaapp.com/maihfzolvngpdA/img/untitled-1.png"
                />

                {/* Username input */}
                <div className="absolute w-[300px] top-[532px] left-[569px]">
                  <Input
                    className="h-10 rounded-md border border-solid border-[#00000029] pl-3.5 py-[11px]"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                {/* Password input */}
                <div className="absolute w-[300px] top-[603px] left-[569px]">
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

                {/* Remember me checkbox */}
                <div className="absolute flex items-center gap-2 top-[652px] left-[578px]">
                  <Checkbox
                    id="remember"
                    className="w-[13px] h-[13px] rounded-sm border border-solid border-[#00000042]"
                  />
                  <label
                    htmlFor="remember"
                    className="font-['Open_Sans',Helvetica] font-normal text-[#000000de] text-[11px] text-center tracking-[0] leading-[normal]"
                  >
                    Remember
                  </label>
                </div>

                {/* Forgot password link */}
                <div className="absolute w-[103px] h-[13px] top-[652px] left-[756px]">
                  <button
                    type="button"
                    className="font-['Open_Sans',Helvetica] font-normal text-[#000000de] text-[11px] text-center tracking-[0] leading-[normal] hover:underline"
                  >
                    Forgot password
                  </button>
                </div>

                {/* Continue button */}
                <Button
                  type="submit"
                  className="absolute w-[168px] h-[41px] top-[715px] left-[636px] bg-[#2196f3] hover:bg-[#1976d2]"
                >
                  <div className="relative w-28 h-[19px] flex items-center justify-center">
                    <div className="font-['Open_Sans',Helvetica] font-semibold text-white text-sm text-center tracking-[0] leading-[normal]">
                      CONTINUE
                    </div>
                  </div>
                </Button>

                {/* Divider with text */}
                <div className="absolute w-[529px] h-[27px] top-[461px] left-[456px] flex items-center">
                  <Separator className="w-[149px] h-[3px]" />
                  <div className="mx-4 font-['Open_Sans',Helvetica] font-normal text-[#0000008a] text-xl text-center tracking-[0] leading-[normal]">
                    Or sign in with email
                  </div>
                  <Separator className="w-[149px] h-[3px]" />
                </div>

                {/* Social login buttons */}
                <div className="absolute flex gap-6 w-[510px] top-[385px] left-[466px] h-9">
                  {socialLogins.map((social, index) => (
                    <Button
                      key={index}
                      type="button"
                      variant="outline"
                      className={`w-[154px] h-9 rounded-[18px] border border-solid flex items-center justify-center`}
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
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};


