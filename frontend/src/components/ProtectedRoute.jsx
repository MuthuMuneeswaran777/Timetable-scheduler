import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

const ProtectedRoute = ({ children }) => {
  console.log('ProtectedRoute checking authentication...');
  
  try {
    const isAuthenticated = authService.isAuthenticated();
    console.log('Is authenticated:', isAuthenticated);
    
    if (!isAuthenticated) {
      console.log('Not authenticated, redirecting to login');
      return <Navigate to="/login" replace />;
    }
    
    console.log('Authenticated, rendering children');
    return children;
  } catch (error) {
    console.error('Error in ProtectedRoute:', error);
    return <Navigate to="/login" replace />;
  }
};

export default ProtectedRoute;
