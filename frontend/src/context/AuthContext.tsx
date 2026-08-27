import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  tenant_id: string;
  is_superuser: boolean;
  roles: string[];
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('nexerp_access_token');
    const savedUser = localStorage.getItem('nexerp_user');

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('nexerp_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = (token: string, userData: User) => {
    localStorage.setItem('nexerp_access_token', token);
    localStorage.setItem('nexerp_user', JSON.stringify(userData));
    localStorage.setItem('nexerp_tenant_id', userData.tenant_id);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('nexerp_access_token');
    localStorage.removeItem('nexerp_user');
    setUser(null);
    window.location.href = '/login';
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.is_superuser || user.permissions.includes('*') || user.permissions.includes('admin:all')) {
      return true;
    }
    return user.permissions.includes(permission);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
