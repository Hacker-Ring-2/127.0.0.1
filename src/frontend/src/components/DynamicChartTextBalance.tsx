/**
 * Clean Dynamic Chart/Text Balance System for TheNZT AI System  
 * Implements Step 3: Customize Chart/Text Balance (20 points)
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, 
  FileText, 
  Settings,
  TrendingUp,
  Info
} from 'lucide-react';

// Import existing TheNZT UI components
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

// Simple Badge component
const Badge: React.FC<{ variant?: string; className?: string; children: React.ReactNode }> = ({ 
  variant = 'default', 
  className = '', 
  children 
}) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
    variant === 'secondary' ? 'bg-gray-100 text-gray-800' : 'bg-blue-100 text-blue-800'
  } ${className}`}>
    {children}
  </span>
);

// Types
interface PreferenceData {
  preference: 'visual' | 'text' | 'mixed' | 'unclear';
  confidence: number;
  reasoning: string;
  keywords_found: string[];
}

interface BalanceConfig {
  chartSize: 'small' | 'medium' | 'large';
  textSize: 'brief' | 'balanced' | 'detailed';
  layout: 'visual-first' | 'text-first' | 'balanced';
  emphasis: 'charts' | 'text' | 'equal';
}

interface DynamicChartTextBalanceProps {
  preferences: PreferenceData;
  chartContent?: React.ReactNode;
  textContent?: string;
  title?: string;
  onBalanceChange?: (config: BalanceConfig) => void;
  className?: string;
}

const DynamicChartTextBalance: React.FC<DynamicChartTextBalanceProps> = ({
  preferences,
  chartContent,
  textContent = '',
  title = 'Dynamic Analysis',
  onBalanceChange,
  className = ''
}) => {
  const [currentConfig, setCurrentConfig] = useState<BalanceConfig | null>(null);

  // Calculate balance configuration
  const balanceConfig = useMemo((): BalanceConfig => {
    const { preference, confidence } = preferences;
    
    switch (preference) {
      case 'visual':
        return {
          chartSize: confidence > 0.8 ? 'large' : 'medium',
          textSize: 'brief',
          layout: 'visual-first',
          emphasis: 'charts'
        };
      case 'text':
        return {
          chartSize: 'small',
          textSize: confidence > 0.8 ? 'detailed' : 'balanced',
          layout: 'text-first',
          emphasis: 'text'
        };
      case 'mixed':
        return {
          chartSize: 'medium',
          textSize: 'balanced',
          layout: 'balanced',
          emphasis: 'equal'
        };
      default:
        return {
          chartSize: 'medium',
          textSize: 'balanced',
          layout: 'balanced',
          emphasis: 'equal'
        };
    }
  }, [preferences]);

  // Update configuration
  useEffect(() => {
    setCurrentConfig(balanceConfig);
    onBalanceChange?.(balanceConfig);
  }, [balanceConfig, onBalanceChange]);

  // Get preference visualization
  const getPreferenceVisualization = () => {
    const { preference, confidence } = preferences;
    const confidencePercent = Math.round(confidence * 100);
    
    return {
      icon: preference === 'visual' ? <BarChart3 className="w-4 h-4" /> :
            preference === 'text' ? <FileText className="w-4 h-4" /> :
            <Info className="w-4 h-4" />,
      color: preference === 'visual' ? 'default' : 'secondary',
      label: `${preference.toUpperCase()} (${confidencePercent}%)`
    };
  };

  // Process text content
  const processedTextContent = useMemo(() => {
    if (!textContent) return '';

    switch (balanceConfig.textSize) {
      case 'brief':
        const sentences = textContent.split('. ').slice(0, 2);
        return sentences.join('. ') + (sentences.length < textContent.split('. ').length ? '...' : '');
      case 'detailed':
        return textContent;
      case 'balanced':
      default:
        const words = textContent.split(' ');
        return words.length > 100 ? words.slice(0, 100).join(' ') + '...' : textContent;
    }
  }, [textContent, balanceConfig.textSize]);

  const preferenceViz = getPreferenceVisualization();

  return (
    <div className={`dynamic-chart-text-balance w-full space-y-4 ${className}`}>
      {/* Header */}
      <Card className="border-2 border-gray-200 shadow-lg">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-[#4B9770]" />
              {title}
            </CardTitle>
            <Badge variant={preferenceViz.color} className="flex items-center gap-1">
              {preferenceViz.icon}
              {preferenceViz.label}
            </Badge>
          </div>
          
          {preferences.reasoning && (
            <p className="text-sm text-gray-600 mt-2 italic">
              🧠 AI Reasoning: {preferences.reasoning}
            </p>
          )}
        </CardHeader>
      </Card>

      {/* Main Content */}
      <div className={`grid gap-4 ${
        balanceConfig.layout === 'balanced' ? 'md:grid-cols-2' : 'grid-cols-1'
      }`}>
        
        {/* Chart Section */}
        {chartContent && (
          <Card className={`${
            balanceConfig.emphasis === 'charts' ? 'ring-2 ring-[#4B9770] ring-opacity-50' : ''
          } ${
            balanceConfig.layout === 'text-first' ? 'order-2' : 'order-1'
          }`}>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <TrendingUp className="w-5 h-5 text-[#4B9770]" />
                Data Visualization
                {balanceConfig.emphasis === 'charts' && (
                  <Badge variant="default" className="ml-2">
                    Primary Focus
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div style={{
                height: balanceConfig.chartSize === 'large' ? '400px' :
                        balanceConfig.chartSize === 'medium' ? '300px' : '200px',
                transition: 'height 0.3s ease-in-out'
              }}>
                {chartContent}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Text Section */}
        {textContent && (
          <Card className={`${
            balanceConfig.emphasis === 'text' ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
          } ${
            balanceConfig.layout === 'visual-first' ? 'order-2' : 'order-1'
          }`}>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="w-5 h-5 text-blue-600" />
                Analysis & Insights
                {balanceConfig.emphasis === 'text' && (
                  <Badge variant="secondary" className="ml-2">
                    Primary Focus
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <div dangerouslySetInnerHTML={{ 
                  __html: processedTextContent.replace(/\n/g, '<br>') 
                }} />
                
                {balanceConfig.textSize === 'brief' && textContent.length > processedTextContent.length && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-3 text-[#4B9770] border-[#4B9770] hover:bg-[#4B9770] hover:text-white"
                  >
                    Show More Details
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Debug Panel */}
      {process.env.NODE_ENV === 'development' && currentConfig && (
        <Card className="border-dashed border-gray-300 bg-gray-50">
          <CardContent className="pt-4">
            <div className="text-xs font-mono text-gray-600 space-y-1">
              <div><strong>Layout:</strong> {currentConfig.layout}</div>
              <div><strong>Chart Size:</strong> {currentConfig.chartSize}</div>
              <div><strong>Text Size:</strong> {currentConfig.textSize}</div>
              <div><strong>Emphasis:</strong> {currentConfig.emphasis}</div>
              <div><strong>Confidence:</strong> {(preferences.confidence * 100).toFixed(1)}%</div>
              <div><strong>Keywords:</strong> {preferences.keywords_found.join(', ')}</div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DynamicChartTextBalance;
export type { PreferenceData, BalanceConfig };