import useFlowStore from "@/stores/flowStore";
import { useState } from "react";
import PublishDropdown from "./deploy-dropdown";
import PlaygroundButton from "./playground-button";
import WebsiteButton from "./website-button";

export default function FlowToolbarOptions() {
  const [open, setOpen] = useState<boolean>(false);
  const hasIO = useFlowStore((state) => state.hasIO);
  const hasWebsite = useFlowStore((state) => state.hasWebsite);
  const websiteUrl = useFlowStore((state) => state.websiteUrl);

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex h-full w-full gap-1.5 rounded-sm transition-all">
        <PlaygroundButton
          hasIO={hasIO}
          open={open}
          setOpen={setOpen}
          canvasOpen
        />
      </div>
      {hasWebsite && websiteUrl && (
        <div className="flex h-full w-full gap-1.5 rounded-sm transition-all">
          <WebsiteButton websiteUrl={websiteUrl} />
        </div>
      )}
      <PublishDropdown />
    </div>
  );
}
