import BotbusinessLogo from "@/assets/BotbusinessLogo.svg?react";

export default function LogoIcon() {
  return (
    <div className="relative flex h-8 w-8 items-center justify-center rounded-md bg-muted">
      <div className="flex h-8 w-8 items-center justify-center">
        <BotbusinessLogo
          title="Botbusiness Logo"
          className="absolute h-[18px] w-[18px] dark:invert"
        />
      </div>
    </div>
  );
}
