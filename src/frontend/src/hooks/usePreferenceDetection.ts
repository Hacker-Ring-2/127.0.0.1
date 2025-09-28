import { useState, useCallback } from 'react';
import { axiosInstance } from '@/services/axiosInstance';

interface PreferenceDetectionResult {
  preference: 'visual' | 'text' | 'mixed';
  confidence: number;
  message: string;
}

interface UsePreferenceDetectionReturn {
  detectPreference: (inputText: string, sessionId: string, messageId: string) => Promise<PreferenceDetectionResult | null>;
  isDetecting: boolean;
  error: string | null;
}

export const usePreferenceDetection = (): UsePreferenceDetectionReturn => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const detectPreference = useCallback(async (
    inputText: string,
    sessionId: string,
    messageId: string
  ): Promise<PreferenceDetectionResult | null> => {
    if (!inputText.trim()) {
      return null;
    }

    try {
      setIsDetecting(true);
      setError(null);

      const response = await axiosInstance.post('/update_personalization', {
        input_text: inputText,
        session_id: sessionId,
        message_id: messageId
      });

      return response.data;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Failed to detect preference';
      
      console.error('Preference detection error:', err);
      setError(errorMessage);
      return null;
    } finally {
      setIsDetecting(false);
    }
  }, []);

  return {
    detectPreference,
    isDetecting,
    error
  };
};

export default usePreferenceDetection;