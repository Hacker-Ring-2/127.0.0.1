'use client';
import { useMemo, useState, useEffect, useCallback } from 'react';
import { PlotlyChart } from './PlotilyChart';
import PreferenceAwareChart from './PreferenceAwareChart';
import { getUUID } from '@/utils/utility';
import { getSupportedChartTypes } from '@/utils/plotly';
import { axiosInstance } from '@/services/axiosInstance';
import { Settings, BarChart3 } from 'lucide-react';

// Type definitions
interface ChartData {
  chart_type: string;
  chart_title: string;
  data: unknown[];
  x_label?: string;
  y_label?: string;
}

interface ParsedChartData {
  id: string;
  supportedTypes: string[];
  data: ChartData;
}

interface ChartCollectionData {
  chart_collection: ChartData[];
}

interface PreferenceMetadata {
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
}

interface PreferenceAwareGraphRendererProps {
  codeContent: string;
  userQuery?: string;
  responseMetadata?: PreferenceMetadata;
  enablePreferenceSystem?: boolean;
}

const PreferenceAwareGraphRenderer = ({ 
  codeContent, 
  userQuery,
  responseMetadata,
  enablePreferenceSystem = true 
}: PreferenceAwareGraphRendererProps) => {
  const [userPreference, setUserPreference] = useState<{
    preference: 'visual' | 'text' | 'mixed';
    confidence: number;
  } | null>(null);
  const [showPreferenceControls, setShowPreferenceControls] = useState(false);

  const fetchUserPreferences = useCallback(async () => {
    try {
      const response = await axiosInstance.get('/get_user_preferences');
      setUserPreference(response.data);
    } catch (error) {
      console.warn('Could not fetch user preferences:', error);
      // Try to detect from user query if available
      if (userQuery) {
        detectPreferenceFromQuery(userQuery);
      }
    }
  }, [userQuery]);

  // Fetch user preferences on component mount
  useEffect(() => {
    if (enablePreferenceSystem) {
      fetchUserPreferences();
    }
  }, [enablePreferenceSystem, fetchUserPreferences]);

  const detectPreferenceFromQuery = async (query: string) => {
    try {
      const response = await axiosInstance.post('/detect_preference', {
        text: query
      });
      setUserPreference({
        preference: response.data.preference,
        confidence: response.data.confidence
      });
    } catch (error) {
      console.warn('Could not detect preference from query:', error);
    }
  };

  // Parse the JSON content safely
  const parsedData = useMemo((): ChartCollectionData | null => {
    try {
      return JSON.parse(codeContent) as ChartCollectionData;
    } catch (error) {
      console.error('Failed to parse graph data:', error);
      return null;
    }
  }, [codeContent]);

  // Create datasets object
  const updatedChartData = useMemo((): ParsedChartData[] => {
    if (!parsedData) return [];
    
    const supportedChartTypes =
      parsedData &&
      parsedData.chart_collection.map((chartData: ChartData) => {
        if (chartData.chart_type === 'pie') {
          const response = getSupportedChartTypes(chartData);
          response.push('pie');
          return response;
        }
        return getSupportedChartTypes(chartData);
      });

    if (
      supportedChartTypes.length > 0 &&
      parsedData.chart_collection.length > 0 &&
      supportedChartTypes.length === parsedData.chart_collection.length
    ) {
      const chartData = parsedData.chart_collection.map((data: ChartData, index: number) => {
        return {
          id: getUUID(),
          supportedTypes: supportedChartTypes[index],
          data: data,
        };
      });

      return chartData;
    }

    return [];
  }, [parsedData]);

  // Determine which chart component to use based on preference system availability
  const shouldUsePreferenceAware = enablePreferenceSystem && (
    userPreference || 
    responseMetadata
  );

  // Get effective preference from multiple sources
  const effectivePreference = responseMetadata?.preference || 
                             userPreference?.preference || 
                             'mixed';
  const effectiveConfidence = responseMetadata?.confidence || 
                             userPreference?.confidence || 
                             0.5;

  // Generate chart descriptions for text-preference users
  const generateChartDescription = (chartData: ChartData): string => {
    const { chart_type, chart_title, data } = chartData;
    const dataPoints = data?.length || 0;
    
    return `This ${chart_type} chart titled "${chart_title}" contains ${dataPoints} data series, providing visual representation of the analytical findings discussed in the text above.`;
  };

  // Handle preference override
  const handlePreferenceOverride = async (newPreference: 'visual' | 'text' | 'mixed') => {
    try {
      await axiosInstance.post('/update_user_preference', {
        user_id: 'current_user', // This should come from auth context
        preference: newPreference,
        confidence: 1.0,
        source: 'manual'
      });
      
      setUserPreference({
        preference: newPreference,
        confidence: 1.0
      });
    } catch (error) {
      console.error('Failed to update preference:', error);
    }
  };

  if (!parsedData || updatedChartData.length === 0) {
    return (
      <div className="my-6 p-6 border-2 border-dashed border-gray-300 rounded-lg text-center">
        <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600 font-medium">No chart data available</p>
        <p className="text-gray-500 text-sm mt-2">
          {effectivePreference === 'visual' 
            ? "I understand you prefer visual content, but chart data couldn't be processed for this response."
            : effectivePreference === 'text'
            ? "Chart data unavailable - detailed analysis provided in text above."
            : "Chart data could not be processed - please refer to text analysis."
          }
        </p>
      </div>
    );
  }

  return (
    <div className="my-6 rounded-lg">
      {/* Preference system controls */}
      {enablePreferenceSystem && (userPreference || responseMetadata) && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                Chart Display: {effectivePreference === 'visual' ? 'Visual Priority' : 
                                effectivePreference === 'text' ? 'Text Supporting' : 'Balanced'}
              </span>
              <span className="text-xs text-gray-500">
                ({Math.round(effectiveConfidence * 100)}% confidence)
              </span>
            </div>
            
            <button
              onClick={() => setShowPreferenceControls(!showPreferenceControls)}
              className="flex items-center gap-1 text-xs bg-white border border-gray-300 px-2 py-1 rounded hover:bg-gray-50"
            >
              <Settings className="h-3 w-3" />
              {showPreferenceControls ? 'Hide' : 'Customize'}
            </button>
          </div>
          
          {showPreferenceControls && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-600">Override preference:</span>
                <button
                  onClick={() => handlePreferenceOverride('visual')}
                  className={`text-xs px-2 py-1 rounded font-medium ${
                    effectivePreference === 'visual'
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  Visual
                </button>
                <button
                  onClick={() => handlePreferenceOverride('text')}
                  className={`text-xs px-2 py-1 rounded font-medium ${
                    effectivePreference === 'text'
                      ? 'bg-green-600 text-white'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}
                >
                  Text Support
                </button>
                <button
                  onClick={() => handlePreferenceOverride('mixed')}
                  className={`text-xs px-2 py-1 rounded font-medium ${
                    effectivePreference === 'mixed'
                      ? 'bg-purple-600 text-white'
                      : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                  }`}
                >
                  Balanced
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chart rendering */}
      <div className="space-y-10">
        {updatedChartData.map((chartData: ParsedChartData) => {
          return (
            <div key={chartData.id}>
              {shouldUsePreferenceAware ? (
                <PreferenceAwareChart
                  chartData={chartData.data}
                  preference={effectivePreference}
                  confidence={effectiveConfidence}
                  showSizeControls={true}
                  chartDescription={generateChartDescription(chartData.data)}
                  fallbackMessage={
                    effectivePreference === 'visual'
                      ? "Visual content prioritized but this chart couldn't be rendered. Please see analysis above."
                      : effectivePreference === 'text'
                      ? "Supporting visualization unavailable - detailed text analysis provided above."
                      : "Chart unavailable - please refer to comprehensive analysis in text sections."
                  }
                  chartType={chartData.data.chart_type}
                  showTitle={effectivePreference !== 'text'}
                  className="transition-all duration-300"
                />
              ) : (
                <div className="bg-white overflow-hidden border rounded-lg">
                  <PlotlyChart
                    chartData={chartData.data}
                    chartType={chartData.data.chart_type}
                    showTitle={true}
                    className="transition-all duration-300"
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Preference system metadata display for debugging/transparency */}
      {responseMetadata && responseMetadata.fallback_applied && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
          <p className="text-yellow-800 font-medium">⚠️ Edge Case Handling Applied</p>
          <p className="text-yellow-700 mt-1">
            The preference system applied fallback formatting to ensure optimal display for your preferences.
          </p>
        </div>
      )}
    </div>
  );
};

// Backward compatibility - enhanced version of the original GraphRenderer
const GraphRenderer = ({ codeContent }: { codeContent: string }) => {
  return (
    <PreferenceAwareGraphRenderer 
      codeContent={codeContent}
      enablePreferenceSystem={true}
    />
  );
};

export default GraphRenderer;
export { PreferenceAwareGraphRenderer };