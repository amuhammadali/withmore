import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AdminRoot } from "./admin/AdminApp";
import { LangProvider } from "./i18n";
import "./index.css";
import { MiniAppRoot } from "./miniapp/MiniApp";
import { ToastProvider } from "./ui";

function App() {
  return (
    <LangProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/miniapp/*" element={<MiniAppRoot />} />
            <Route path="/admin/*" element={<AdminRoot />} />
            <Route path="/dashboard" element={<Navigate to="/admin" replace />} />
            <Route path="/products" element={<Navigate to="/admin/products" replace />} />
            <Route path="/orders" element={<Navigate to="/admin/orders" replace />} />
            <Route path="/crm" element={<Navigate to="/admin/crm" replace />} />
            <Route path="/customers" element={<Navigate to="/admin/customers" replace />} />
            <Route path="/promotions" element={<Navigate to="/admin/promotions" replace />} />
            <Route path="/settings" element={<Navigate to="/admin/settings" replace />} />
            <Route path="/marketing" element={<Navigate to="/admin/marketing" replace />} />
            <Route path="/growth" element={<Navigate to="/admin/growth" replace />} />
            <Route path="/content" element={<Navigate to="/admin/content" replace />} />
            <Route path="/team" element={<Navigate to="/admin/team" replace />} />
            <Route path="/activity" element={<Navigate to="/admin/audit" replace />} />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </LangProvider>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
