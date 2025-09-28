import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, FileText, BarChart3, Settings } from 'lucide-react';
import { axiosInstance } from '@/services/axiosInstance';

// Simple Badge component
const Badge: React.FC<{ className?: string; children: React.ReactNode }> = ({ className, children }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
    {children}
  </span>
);

interface UserPreference {
  preference: 'visual' | 'text' | 'mixed';
  confidence: number;
  last_updated?: string;
  detection_count?: number;
}

const PreferenceManager: React.FC = () => {
  const [preferences, setPreferences] = useState<UserPreference | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/get_user_preferences');
      setPreferences(response.data);
      setError(null);
    } catch (err: unknown) {
      console.error('Error fetching preferences:', err);
      const errorMessage = err instanceof Error && 'response' in err 
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to load preferences'
        : 'Failed to load preferences';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPreferences();
  }, []);

  const getPreferenceIcon = (preference: string) => {
    switch (preference) {
      case 'visual':
        return <BarChart3 className="h-5 w-5" />;
      case 'text':
        return <FileText className="h-5 w-5" />;
      default:
        return <Eye className="h-5 w-5" />;
    }
  };

  const getPreferenceBadgeColor = (preference: string) => {
    switch (preference) {
      case 'visual':
        return 'bg-blue-100 text-blue-800';
      case 'text':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { level: 'High', color: 'bg-green-500' };
    if (confidence >= 0.6) return { level: 'Medium', color: 'bg-yellow-500' };
    return { level: 'Low', color: 'bg-red-500' };
  };

  if (loading) {
    return (
      <Card className="w-full max-w-md">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-md">
        <CardContent className="p-6">
          <div className="text-center text-red-600">
            <p>{error}</p>
            <Button onClick={fetchPreferences} className="mt-2" variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Response Preferences
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {preferences ? (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Current Preference:</span>
              <Badge className={`flex items-center gap-1 ${getPreferenceBadgeColor(preferences.preference)}`}>
                {getPreferenceIcon(preferences.preference)}
                {preferences.preference.charAt(0).toUpperCase() + preferences.preference.slice(1)}
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Confidence:</span>
              <div className="flex items-center gap-2">
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getConfidenceLevel(preferences.confidence).color}`}
                    style={{ width: `${preferences.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600">
                  {getConfidenceLevel(preferences.confidence).level}
                </span>
              </div>
            </div>

            {preferences.detection_count && preferences.detection_count > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Detections:</span>
                <span className="text-sm text-gray-600">{preferences.detection_count}</span>
              </div>
            )}

            {preferences.last_updated && (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Last Updated:</span>
                <span className="text-sm text-gray-600">
                  {new Date(preferences.last_updated).toLocaleDateString()}
                </span>
              </div>
            )}

            <div className="pt-2 border-t">
              <p className="text-xs text-gray-500">
                Your preferences are automatically detected from your messages to provide better responses.
              </p>
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500">
            <p className="text-sm">No preferences detected yet.</p>
            <p className="text-xs mt-2">
              Start chatting to help us understand your preferred response format!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PreferenceManager;