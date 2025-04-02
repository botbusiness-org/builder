import { AuthContext } from "@/contexts/authContext";
import { CustomNavigate } from "@/customization/components/custom-navigate";
import { LoadingPage } from "@/pages/LoadingPage";
import useAuthStore from "@/stores/authStore";
import { useUtilityStore } from "@/stores/utilityStore";
import { useContext } from "react";

export const ProtectedAdminRoute = ({ children }) => {
  const { userData } = useContext(AuthContext);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const autoLogin = useAuthStore((state) => state.autoLogin);
  const isAdmin = useAuthStore((state) => state.isAdmin);
  const featureFlags = useUtilityStore((state) => state.featureFlags);

  if (!isAuthenticated) {
    return <LoadingPage />;
  } else if ((userData && !isAdmin) || autoLogin || !featureFlags?.admin_page) {
    return <CustomNavigate to="/" replace />;
  } else {
    return children;
  }
};
