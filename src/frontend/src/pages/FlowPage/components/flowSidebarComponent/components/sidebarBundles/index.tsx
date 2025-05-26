import ForwardedIconComponent from "@/components/common/genericIconComponent";
import {
  Disclosure,
  DisclosureContent,
  DisclosureTrigger,
} from "@/components/ui/disclosure";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
} from "@/components/ui/sidebar";
import { memo, useMemo } from "react";
import { SidebarGroupProps } from "../../types";
import { BundleItem } from "../bundleItems";

export const MemoizedSidebarGroup = memo(
  ({
    BUNDLES,
    search,
    sortedCategories,
    dataFilter,
    nodeColors,
    onDragStart,
    sensitiveSort,
    openCategories,
    setOpenCategories,
    handleKeyDownInput,
    uniqueInputsComponents,
  }: SidebarGroupProps) => {
    const sortedBundles = useMemo(() => {
      return BUNDLES.toSorted((a, b) => {
        const referenceArray = search !== "" ? sortedCategories : BUNDLES;
        return (
          referenceArray.findIndex((value) => value === a.name) -
          referenceArray.findIndex((value) => value === b.name)
        );
      });
    }, [BUNDLES, search, sortedCategories]);

    return (
      <Disclosure
        key="bundles"
        open={openCategories.includes("bundles")}
        onOpenChange={(isOpen) => {
          setOpenCategories((prev) =>
            isOpen
              ? [...prev, "bundles"]
              : prev.filter((cat) => cat !== "bundles"),
          );
        }}
      >
        <SidebarGroup className="px-3">
          <DisclosureTrigger className="group/collapsible">
            <SidebarMenuButton asChild>
              <div
                tabIndex={0}
                onKeyDown={(e) => handleKeyDownInput(e, "bundles")}
                className="flex cursor-pointer items-center gap-2"
                data-testid="disclosure-bundles-bundles"
              >
                <ForwardedIconComponent
                  name="external-link"
                  className="h-4 w-4 text-muted-foreground group-aria-expanded/collapsible:text-primary"
                />
                <span className="flex-1 group-aria-expanded/collapsible:font-semibold">
                  External Services
                </span>
                <ForwardedIconComponent
                  name="ChevronRight"
                  className="-mr-1 h-4 w-4 text-muted-foreground transition-all group-aria-expanded/collapsible:rotate-90"
                />
              </div>
            </SidebarMenuButton>
          </DisclosureTrigger>
          <DisclosureContent>
            <SidebarGroupContent>
              <SidebarMenu>
                {sortedBundles.map((item) => (
                  <BundleItem
                    key={item.name}
                    item={item}
                    isOpen={openCategories.includes(item.name)}
                    onOpenChange={(isOpen) => {
                      setOpenCategories((prev) =>
                        isOpen
                          ? [...prev, item.name]
                          : prev.filter((cat) => cat !== item.name),
                      );
                    }}
                    dataFilter={dataFilter}
                    nodeColors={nodeColors}
                    uniqueInputsComponents={uniqueInputsComponents}
                    onDragStart={onDragStart}
                    sensitiveSort={sensitiveSort}
                    handleKeyDownInput={handleKeyDownInput}
                  />
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </DisclosureContent>
        </SidebarGroup>
      </Disclosure>
    );
  },
);

MemoizedSidebarGroup.displayName = "MemoizedSidebarGroup";

export default MemoizedSidebarGroup;
