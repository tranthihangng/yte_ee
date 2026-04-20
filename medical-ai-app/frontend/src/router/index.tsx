import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import { DashboardPage } from "../pages/DashboardPage";
import { HelpPage } from "../pages/HelpPage";
import { HistoryPage } from "../pages/HistoryPage";
import { NewAnalysisPage } from "../pages/NewAnalysisPage";
import { ReportPage } from "../pages/ReportPage";
import { SettingsPage } from "../pages/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "analysis", element: <NewAnalysisPage /> },
      { path: "history", element: <HistoryPage /> },
      { path: "reports", element: <ReportPage /> },
      { path: "settings", element: <SettingsPage /> },
      { path: "help", element: <HelpPage /> }
    ]
  }
]);
