import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { WEBSITE_BUTTON_NAME } from "@/constants/constants";
import { ENABLE_PUBLISH } from "@/customization/feature-flags";

interface WebsiteButtonProps {
  websiteUrl: string;
}

const ButtonIcon = () => (
  <ForwardedIconComponent
    name="website"
    className="h-4 w-4 transition-all"
    strokeWidth={ENABLE_PUBLISH ? 2 : 1.5}
  />
);

const ButtonLabel = () => (
  <span className="hidden md:block">{WEBSITE_BUTTON_NAME}</span>
);

const WebsiteButton = ({ websiteUrl }: WebsiteButtonProps) => (
  <div
    data-testid="website-btn-flow-io"
    className="playground-btn-flow-toolbar cursor-pointer hover:bg-accent"
    onClick={() => window.open(websiteUrl, "_blank")}
  >
    <ButtonIcon />
    <ButtonLabel />
  </div>
);

export default WebsiteButton;
