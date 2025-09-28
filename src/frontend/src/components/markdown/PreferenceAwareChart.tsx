import React from 'react';
import { PlotlyChartProps } from '@/types/ploytly-types';
import { PlotlyChart } from './PlotilyChart';
import { BarChart3, Maximize2, Minimize2, Info } from 'lucide-react';

interface PreferenceAwareChartProps extends PlotlyChartProps {
  preference?: 'visual' | 'text' | 'mixed';
  confidence?: number;
  showSizeControls?: boolean;
  chartDescription?: string;
  fallbackMessage?: string;
}

const PreferenceAwareChart: React.FC<PreferenceAwareChartProps> = ({
  chartData,
  preference = 'mixed',
  confidence = 0.5,
  showSizeControls = true,
  chartDescription,
  fallbackMessage,
  ...plotlyProps
}) => {
  const [currentSize, setCurrentSize] = React.useState<'small' | 'medium' | 'large'>(
    preference === 'visual' ? 'large' : preference === 'text' ? 'small' : 'medium'
  );
  const [showDescription, setShowDescription] = React.useState(preference === 'text');

  // Dynamic sizing based on preference
  const getSizeConfig = (size: string, preference: string) => {
    const configs = {
      visual: {
        small: { width: '100%', height: 400 },
        medium: { width: '100%', height: 550 }, 
        large: { width: '100%', height: 700 }
      },
      text: {
        small: { width: '100%', height: 250 },
        medium: { width: '100%', height: 350 },
        large: { width: '100%', height: 450 }
      },
      mixed: {
        small: { width: '100%', height: 300 },
        medium: { width: '100%', height: 450 },
        large: { width: '100%', height: 600 }
      }
    };

    return configs[preference as keyof typeof configs]?.[size as keyof typeof configs.visual] || 
           configs.mixed[size as keyof typeof configs.mixed];
  };

  const currentConfig = getSizeConfig(currentSize, preference);

  // Preference-specific styling
  const getChartContainer = () => {
    const baseClasses = "rounded-lg border transition-all duration-300";
    
    switch (preference) {
      case 'visual':
        return `${baseClasses} border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-4 shadow-lg`;
      case 'text':
        return `${baseClasses} border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 p-2 shadow-sm`;
      case 'mixed':
      default:
        return `${baseClasses} border-gray-200 bg-gradient-to-br from-gray-50 to-slate-50 p-3 shadow-md`;
    }
  };

  const getPreferenceLabel = () => {
    const labels = {
      visual: { text: 'Visual Optimized', color: 'text-blue-700', bg: 'bg-blue-100' },
      text: { text: 'Text Supporting', color: 'text-green-700', bg: 'bg-green-100' },
      mixed: { text: 'Balanced View', color: 'text-purple-700', bg: 'bg-purple-100' }
    };
    
    return labels[preference] || labels.mixed;
  };

  // Error fallback with preference-aware messaging
  if (!chartData || !chartData.data) {
    const label = getPreferenceLabel();
    
    return (
      <div className={getChartContainer()}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Chart Not Available</span>
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${label.bg} ${label.color}`}>
            {label.text}
          </span>
        </div>
        
        <div 
          className="flex items-center justify-center bg-white border-2 border-dashed border-gray-300 rounded-lg"
          style={{ height: currentConfig.height }}
        >
          <div className="text-center p-6">
            {preference === 'visual' ? (
              <>
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 font-medium">Visual content requested but unavailable</p>
                <p className="text-gray-500 text-sm mt-2">
                  I understand you prefer charts and graphs. The data for this visualization 
                  couldn&apos;t be processed, but I&apos;ve provided alternative insights above.
                </p>
              </>
            ) : preference === 'text' ? (
              <>
                <Info className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Supporting chart unavailable</p>
                <p className="text-gray-500 text-xs mt-1">
                  Detailed text analysis provided above
                </p>
              </>
            ) : (
              <>
                <BarChart3 className="h-10 w-10 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">Chart data unavailable</p>
                <p className="text-gray-500 text-sm mt-1">
                  {fallbackMessage || "Please refer to the text analysis for insights"}
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  const label = getPreferenceLabel();

  return (
    <div className={getChartContainer()}>
      {/* Chart header with preference indicator and controls */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">
            {chartData.chart_title || 'Data Visualization'}
          </span>
          {confidence && (
            <span className="text-xs text-gray-500">
              ({Math.round(confidence * 100)}% confidence)
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-1 rounded-full ${label.bg} ${label.color}`}>
            {label.text}
          </span>
          
          {showSizeControls && (
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={() => setCurrentSize('small')}
                className={`p-1 rounded text-xs ${
                  currentSize === 'small' 
                    ? 'bg-gray-200 text-gray-700' 
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
                title="Small chart"
              >
                <Minimize2 className="h-3 w-3" />
              </button>
              <button
                onClick={() => setCurrentSize('medium')}
                className={`p-1 rounded text-xs ${
                  currentSize === 'medium' 
                    ? 'bg-gray-200 text-gray-700' 
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
                title="Medium chart"
              >
                <BarChart3 className="h-3 w-3" />
              </button>
              <button
                onClick={() => setCurrentSize('large')}
                className={`p-1 rounded text-xs ${
                  currentSize === 'large' 
                    ? 'bg-gray-200 text-gray-700' 
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
                title="Large chart"
              >
                <Maximize2 className="h-3 w-3" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Chart description for text preference users */}
      {chartDescription && preference === 'text' && (
        <div className="mb-3 p-3 bg-white border border-green-200 rounded text-sm">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-green-800">Chart Description</p>
              <p className="text-green-700 mt-1">{chartDescription}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main chart */}
      <div className="bg-white rounded border">
        <PlotlyChart
          chartData={chartData}
          width={currentConfig.width}
          height={currentConfig.height}
          showTitle={preference !== 'text'} // Hide title for text users to save space
          {...plotlyProps}
        />
      </div>

      {/* Chart insights footer for text preference users */}
      {preference === 'text' && chartData.data && (
        <div className="mt-3 p-3 bg-white border border-green-200 rounded text-sm">
          <button
            onClick={() => setShowDescription(!showDescription)}
            className="flex items-center gap-2 text-green-700 hover:text-green-800 font-medium"
          >
            <Info className="h-4 w-4" />
            {showDescription ? 'Hide' : 'Show'} Chart Analysis
          </button>
          
          {showDescription && (
            <div className="mt-2 space-y-2 text-green-700">
              <p>
                <strong>Data Points:</strong> {chartData.data.length} series
              </p>
              <p>
                <strong>Chart Type:</strong> {chartData.chart_type || 'Standard visualization'}
              </p>
              {chartData.x_label && (
                <p><strong>X-Axis:</strong> {chartData.x_label}</p>
              )}
              {chartData.y_label && (
                <p><strong>Y-Axis:</strong> {chartData.y_label}</p>
              )}
              <p className="text-xs text-green-600 mt-2">
                This chart supports the detailed analysis provided in the text sections above.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Visual enhancement for visual preference users */}
      {preference === 'visual' && currentSize === 'large' && (
        <div className="mt-2 text-center">
          <p className="text-xs text-blue-600">
            📊 Optimized for visual analysis • Interactive chart • Click and drag to explore
          </p>
        </div>
      )}
    </div>
  );
};

export default PreferenceAwareChart;