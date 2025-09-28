import React, { useState, useEffect } from 'react';
import { Eye, FileText, BarChart3 } from 'lucide-react';
import { axiosInstance } from '@/services/axiosInstance';

interface PreferenceAwareResponseProps {
  children: React.ReactNode;
  messageId?: string;
  responseMetadata?: {
    preference: 'visual' | 'text' | 'mixed';
    confidence: number;
    formatting_applied: string;
    content_summary: string;
    fallback_applied: boolean;
    metadata: {
      chart_count: number;
      text_sections: number;
      preference_keywords: string[];
    };
  };
}

interface UserPreference {
  preference: 'visual' | 'text' | 'mixed';
  confidence: number;
}

const PreferenceAwareResponse: React.FC<PreferenceAwareResponseProps> = ({ 
  children, 
  messageId,
  responseMetadata
}) => {
  const [userPreference, setUserPreference] = useState<UserPreference | null>(null);
  const [showPreferenceHint, setShowPreferenceHint] = useState(false);
  const [showFormatDetails, setShowFormatDetails] = useState(false);

  useEffect(() => {
    const fetchUserPreferences = async () => {
      try {
        const response = await axiosInstance.get('/get_user_preferences');
        setUserPreference(response.data);
        
        // Show hint if confidence is low
        if (response.data.confidence < 0.6) {
          setShowPreferenceHint(true);
        }
      } catch (error) {
        console.warn('Could not fetch user preferences:', error);
      }
    };

    fetchUserPreferences();
  }, [messageId]);

  const getPreferenceIcon = (preference: string) => {
    switch (preference) {
      case 'visual':
        return <BarChart3 className="h-4 w-4 text-blue-600" />;
      case 'text':
        return <FileText className="h-4 w-4 text-green-600" />;
      default:
        return <Eye className="h-4 w-4 text-gray-600" />;
    }
  };

  const getPreferenceMessage = (preference: string, confidence: number, chartCount?: number, textSections?: number) => {
    const confidenceText = confidence > 0.8 ? "highly confident" : confidence > 0.6 ? "confident" : "learning";
    
    switch (preference) {
      case 'visual':
        return `🎯 Visual preference detected (${confidenceText}) - ${chartCount || 0} charts prioritized`;
      case 'text':
        return `📝 Text preference detected (${confidenceText}) - ${textSections || 0} detailed sections`;
      default:
        return `⚖️ Balanced approach (${confidenceText}) - Mixed visual and text content`;
    }
  };

  const getFormattingBadge = (formattingType: string) => {
    const badges = {
      'visual_priority': { text: 'Visual First', color: 'bg-blue-100 text-blue-800', icon: BarChart3 },
      'text_priority': { text: 'Text First', color: 'bg-green-100 text-green-800', icon: FileText },
      'balanced': { text: 'Balanced', color: 'bg-purple-100 text-purple-800', icon: Eye }
    };
    
    return badges[formattingType as keyof typeof badges] || badges.balanced;
  };

  // Use responseMetadata if available, otherwise fallback to userPreference
  const currentPreference = responseMetadata?.preference || userPreference?.preference;
  const currentConfidence = responseMetadata?.confidence || userPreference?.confidence || 0;
  const chartCount = responseMetadata?.metadata?.chart_count || 0;
  const textSections = responseMetadata?.metadata?.text_sections || 0;
  const fallbackApplied = responseMetadata?.fallback_applied || false;
  const formattingApplied = responseMetadata?.formatting_applied;

  return (
    <div className="space-y-3">
      {/* Enhanced preference indicator with metadata */}
      {currentPreference && currentConfidence > 0.5 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border">
            <div className="flex items-center gap-2">
              {getPreferenceIcon(currentPreference)}
              <span className="text-sm font-medium text-gray-800">
                {getPreferenceMessage(currentPreference, currentConfidence, chartCount, textSections)}
              </span>
            </div>
            
            {formattingApplied && (
              <div className="flex items-center gap-2">
                {(() => {
                  const badge = getFormattingBadge(formattingApplied);
                  const IconComponent = badge.icon;
                  return (
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${badge.color} flex items-center gap-1`}>
                      <IconComponent className="h-3 w-3" />
                      {badge.text}
                    </span>
                  );
                })()}
              </div>
            )}
          </div>

          {/* Content statistics */}
          {responseMetadata && (
            <div className="flex items-center gap-4 text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded">
              <span className="flex items-center gap-1">
                <BarChart3 className="h-3 w-3" />
                {chartCount} charts
              </span>
              <span className="flex items-center gap-1">
                <FileText className="h-3 w-3" />
                {textSections} text sections
              </span>
              {fallbackApplied && (
                <span className="text-orange-600 font-medium">⚠️ Fallback applied</span>
              )}
              <button 
                onClick={() => setShowFormatDetails(!showFormatDetails)}
                className="text-blue-600 hover:text-blue-800 font-medium ml-auto"
              >
                {showFormatDetails ? 'Hide details' : 'Show details'}
              </button>
            </div>
          )}

          {/* Detailed formatting information */}
          {showFormatDetails && responseMetadata && (
            <div className="bg-white border rounded-lg p-3 text-sm space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium text-gray-700">Summary:</span>
                  <p className="text-gray-600 mt-1">{responseMetadata.content_summary}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Keywords detected:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {responseMetadata.metadata.preference_keywords?.map((keyword, index) => (
                      <span key={index} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {fallbackApplied && (
                <div className="border-t pt-2">
                  <span className="font-medium text-orange-700">Fallback Information:</span>
                  <p className="text-orange-600 mt-1">
                    Edge case handling was applied to ensure optimal response format for your preferences.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Preference learning hint - enhanced */}
      {showPreferenceHint && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 p-4 rounded-lg">
          <div className="flex items-start gap-3">
            <Eye className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-blue-800 font-medium">🚀 AI Response Personalization Active</p>
              <p className="text-blue-700 mt-1 text-sm">
                I&apos;m analyzing your preferences to provide optimal responses:
              </p>
              <ul className="text-blue-700 mt-2 text-sm space-y-1">
                <li>• <strong>Visual preference:</strong> Charts and graphs prioritized</li>
                <li>• <strong>Text preference:</strong> Detailed explanations first</li>
                <li>• <strong>Balanced:</strong> Mixed visual and text content</li>
              </ul>
              <div className="flex items-center gap-2 mt-3">
                <button 
                  onClick={() => setShowPreferenceHint(false)}
                  className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-medium"
                >
                  Got it!
                </button>
                <span className="text-xs text-blue-600">Keep chatting to improve personalization</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main response content */}
      <div className="response-content">
        {children}
      </div>

      {/* Enhanced response format options */}
      {currentPreference && (
        <div className="border-t pt-3 mt-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Response format preferences:</span>
            <div className="flex items-center gap-2">
              <button 
                className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
                  currentPreference === 'visual' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }`}
                onClick={() => {
                  // Future: Request visual format
                }}
              >
                <BarChart3 className="h-3 w-3 inline mr-1" />
                Visual
              </button>
              <button 
                className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
                  currentPreference === 'text' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
                onClick={() => {
                  // Future: Request text format
                }}
              >
                <FileText className="h-3 w-3 inline mr-1" />
                Text
              </button>
              <button 
                className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
                  currentPreference === 'mixed' 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                }`}
                onClick={() => {
                  // Future: Request balanced format
                }}
              >
                <Eye className="h-3 w-3 inline mr-1" />
                Balanced
              </button>
            </div>
          </div>
          
          {/* Confidence indicator */}
          {currentConfidence > 0 && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-gray-500">Confidence:</span>
              <div className="flex-1 bg-gray-200 rounded-full h-1.5 max-w-24">
                <div 
                  className={`h-1.5 rounded-full transition-all ${
                    currentConfidence > 0.8 ? 'bg-green-500' :
                    currentConfidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(currentConfidence * 100, 100)}%` }}
                />
              </div>
              <span className="text-xs text-gray-500">
                {Math.round(currentConfidence * 100)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PreferenceAwareResponse;