import { Navigate } from "react-router-dom";
import * as api from "../api";
import { useEffect, useState } from "react";

const AppEntryPage = () => {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    async function checkAuth() {
      const resp = await api.refresh();

      if (resp.ok) {
        setAuthenticated(true);
      } else {
        setAuthenticated(false);
      }
    }

    checkAuth();
  }, []);

  if (authenticated === null) {
    return null;
  }
  else if (authenticated === true) {
    return <Navigate to="/home" replace />;
  }
  else if (authenticated === false) {
    return <Navigate to="/login" replace />;
  }
};

export default AppEntryPage;
