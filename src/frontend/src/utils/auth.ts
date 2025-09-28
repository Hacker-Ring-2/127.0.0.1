import { axiosInstance } from '@/services/axiosInstance';
import { useAuthStore } from '@/store/useZustandStore';
import Cookies from 'js-cookie';
import { getCookie } from './getCookie';

export const verifyToken = async (): Promise<boolean> => {
  try {
    // Check if we already have a user in the store
    const authStore = useAuthStore.getState();
    if (authStore.isAuthenticated) {
      return true;
    }

    // Get token from localStorage
    const accessToken = getCookie('access_token');
    if (!accessToken) {
      return false;
    }

    // Verify token with API
    console.log('Attempting to verify token with backend...');
    console.log('BASE_URL:', process.env.NEXT_PUBLIC_BASE_URL);
    const user = await axiosInstance.get('/get_user_info');
    console.log('User data received:', user.data);
    
    // Check if user data exists and has required fields
    if (user.data && user.data.full_name && user.data.email) {
      useAuthStore
        .getState()
        .setUser(user.data.full_name, user.data.email, user.data.profile_picture || '');
    } else {
      throw new Error('Invalid user data received from API');
    }
    return true;
  } catch (error) {
    console.error('Token verification failed with full error:', error);
    Cookies.remove('access_token');
    useAuthStore.getState().resetUser();
    return false;
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  useAuthStore.getState().resetUser();
  Cookies.remove('access_token');
  window.location.href = '/login';
};
