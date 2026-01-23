import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

export const ProtectedRoute = ({ children }) => {  // Add 'export' here
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
