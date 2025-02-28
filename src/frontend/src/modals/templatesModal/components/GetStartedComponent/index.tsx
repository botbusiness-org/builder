import BaseModal from "@/modals/baseModal";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { CardData } from "@/types/templates/types";
import ideaImg from "../../../../assets/temp-pat-1.png";
import mvpImg from "../../../../assets/temp-pat-2.png";
import marketingImg from "../../../../assets/temp-pat-3.png";
import ideaHorizontalImg from "../../../../assets/temp-pat-m-1.png";
import mvpHorizontalImg from "../../../../assets/temp-pat-m-2.png";
import marketingHorizontalImg from "../../../../assets/temp-pat-m-3.png";

import TemplateGetStartedCardComponent from "../TemplateGetStartedCardComponent";

export default function GetStartedComponent() {
  const examples = useFlowsManagerStore((state) => state.examples);

  // Define the card data
  const cardData: CardData[] = [
    {
      bgImage: ideaImg,
      bgHorizontalImage: ideaHorizontalImg,
      icon: "rocket",
      category: "Idea & Validation",
      flow: examples.find((example) => example.name === "Find a business idea"),
    },
    {
      bgImage: mvpImg,
      bgHorizontalImage: mvpHorizontalImg,
      icon: "hammer",
      category: "Build & Launch",
      flow: examples.find((example) => example.name === "Build an MVP"),
    },
    {
      bgImage: marketingImg,
      bgHorizontalImage: marketingHorizontalImg,
      icon: "trending-up",
      category: "Growth & Marketing",
      flow: examples.find((example) => example.name === "Automate marketing"),
    },
  ];

  return (
    <div className="flex flex-1 flex-col gap-4 md:gap-8">
      <BaseModal.Header description="Start building a simple automatic business.">
        Get started
      </BaseModal.Header>
      <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-3">
        {cardData.map((card, index) => (
          <TemplateGetStartedCardComponent key={index} {...card} />
        ))}
      </div>
    </div>
  );
}
