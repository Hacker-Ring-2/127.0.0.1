/**
 * Advanced Dynamic Chart/Text Balance System for TheNZT AI System  
 * Implements Step 3: Customize Chart/Text Balance (20 points)
 * 
 * This module provides intelligent chart and text sizing based on user preferences,
 * with comprehensive chart integration and enhanced UI components.
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, 
  FileText, 
  Maximize2,
  Settings,
  TrendingUp,
  Info,
  Activity,
  Eye,
  EyeOff,
  Brain,
  Target
} from 'lucide-react';

// Import existing TheNZT UI components
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

// Import Recharts for advanced chart functionality
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as PieChartComponent,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

// Types and Interfaces
interface PreferenceData {
  preference: 'visual' | 'text' | 'mixed' | 'unclear';
  confidence: number;
  reasoning: string;
  keywords_found: string[];
  context?: {
    user_history?: string[];
    domain?: string;
    complexity?: 'low' | 'medium' | 'high';
  };
}

interface BalanceConfig {
  chartSize: 'small' | 'medium' | 'large' | 'extra-large';
  textSize: 'brief' | 'balanced' | 'detailed' | 'comprehensive';
  layout: 'visual-first' | 'text-first' | 'balanced' | 'side-by-side';
  emphasis: 'charts' | 'text' | 'equal';
  responsiveBreakpoint: 'mobile' | 'tablet' | 'desktop';
}

interface ChartData {
  name: string;
  value: number;
  color?: string;
  category?: string;
}

interface AdvancedPreferenceBalanceProps {
  preferences: PreferenceData;
  chartData?: ChartData[];
  textContent?: string;
  title?: string;
  onBalanceChange?: (config: BalanceConfig) => void;
  onPreferenceOverride?: (newPreference: PreferenceData) => void;
  className?: string;
  showControls?: boolean;
}

// Simple Badge component for compatibility
const Badge: React.FC<{ variant?: string; className?: string; children: React.ReactNode }> = ({ 
  variant = 'default', 
  className = '', 
  children 
}) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
    variant === 'secondary' ? 'bg-gray-100 text-gray-800 border border-gray-200' : 
    variant === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
    variant === 'warning' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
    'bg-blue-100 text-blue-800 border border-blue-200'
  } ${className}`}>
    {children}
  </span>
);

// Enhanced Chart Components
const MultiTypeChart: React.FC<{ 
  data: ChartData[], 
  type: 'line' | 'bar' | 'area' | 'pie',
  size: 'small' | 'medium' | 'large' | 'extra-large'
}> = ({ data, type, size }) => {
  const dimensions = {
    'small': { width: '100%', height: 200 },
    'medium': { width: '100%', height: 300 },
    'large': { width: '100%', height: 400 },
    'extra-large': { width: '100%', height: 500 }
  };

  const colors = ['#4B9770', '#8CC8A8', '#2C5530', '#A8E6CF', '#66B885'];

  const renderChart = (): React.ReactElement => {
    switch (type) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="name" stroke="#666" fontSize={12} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#4B9770" 
              strokeWidth={3}
              dot={{ fill: '#4B9770', strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8, stroke: '#4B9770', strokeWidth: 2 }}
            />
          </LineChart>
        );
      case 'bar':
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="name" stroke="#666" fontSize={12} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
            />
            <Bar dataKey="value" fill="#4B9770" radius={[4, 4, 0, 0]} />
          </BarChart>
        );
      case 'area':
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="name" stroke="#666" fontSize={12} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#4B9770" 
              fill="url(#colorGradient)"
              strokeWidth={2}
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4B9770" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#4B9770" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
          </AreaChart>
        );
      case 'pie':
        return (
          <PieChartComponent>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={size === 'small' ? 60 : size === 'medium' ? 80 : 100}
              fill="#4B9770"
              dataKey="value"
              label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChartComponent>
        );
      default:
        return <div className="flex items-center justify-center h-full text-gray-500">No chart type selected</div>;
    }
  };

  return (
    <div style={{ width: dimensions[size].width, height: dimensions[size].height }}>
      <ResponsiveContainer width="100%" height="100%">
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
};

// Main Component
const AdvancedPreferenceBalance: React.FC<AdvancedPreferenceBalanceProps> = ({
  preferences,
  chartData = [],
  textContent = '',
  title = 'AI-Powered Analysis',
  onBalanceChange,
  onPreferenceOverride,
  className = '',
  showControls = true
}) => {
  const [currentConfig, setCurrentConfig] = useState<BalanceConfig | null>(null);
  const [isInteractive, setIsInteractive] = useState(false);
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area' | 'pie'>('line');
  const [manualOverride, setManualOverride] = useState(false);

  // Calculate optimal balance configuration
  const balanceConfig = useMemo((): BalanceConfig => {
    if (manualOverride && currentConfig) return currentConfig;

    const { preference, confidence } = preferences;
    
    // Enhanced logic based on preference and confidence
    switch (preference) {
      case 'visual':
        return {
          chartSize: confidence > 0.9 ? 'extra-large' : confidence > 0.7 ? 'large' : 'medium',
          textSize: confidence > 0.8 ? 'brief' : 'balanced',
          layout: 'visual-first',
          emphasis: 'charts',
          responsiveBreakpoint: 'desktop'
        };
      case 'text':
        return {
          chartSize: confidence > 0.8 ? 'small' : 'medium',
          textSize: confidence > 0.9 ? 'comprehensive' : confidence > 0.7 ? 'detailed' : 'balanced',
          layout: 'text-first',
          emphasis: 'text',
          responsiveBreakpoint: 'tablet'
        };
      case 'mixed':
        return {
          chartSize: 'medium',
          textSize: 'balanced',
          layout: confidence > 0.7 ? 'side-by-side' : 'balanced',
          emphasis: 'equal',
          responsiveBreakpoint: 'tablet'
        };
      default: // unclear
        return {
          chartSize: 'medium',
          textSize: 'balanced',
          layout: 'balanced',
          emphasis: 'equal',
          responsiveBreakpoint: 'mobile'
        };
    }
  }, [preferences, manualOverride, currentConfig]);

  // Update parent when balance changes
  useEffect(() => {
    setCurrentConfig(balanceConfig);
    onBalanceChange?.(balanceConfig);
  }, [balanceConfig, onBalanceChange]);

  // Preference visualization
  const getPreferenceVisualization = () => {
    const { preference, confidence } = preferences;
    const confidencePercent = Math.round(confidence * 100);
    
    return {
      icon: preference === 'visual' ? <BarChart3 className="w-4 h-4" /> :
            preference === 'text' ? <FileText className="w-4 h-4" /> :
            preference === 'mixed' ? <Activity className="w-4 h-4" /> :
            <Info className="w-4 h-4" />,
      color: preference === 'visual' ? 'success' :
             preference === 'text' ? 'default' :
             preference === 'mixed' ? 'warning' : 'secondary',
      label: `${preference.toUpperCase()} (${confidencePercent}%)`
    };
  };

  // Process text content based on configuration
  const processedTextContent = useMemo(() => {
    if (!textContent) return '';

    switch (balanceConfig.textSize) {
      case 'brief':
        const sentences = textContent.split('. ').slice(0, 2);
        return sentences.join('. ') + (sentences.length < textContent.split('. ').length ? '...' : '');
      case 'comprehensive':
        return textContent;
      case 'detailed':
        const words = textContent.split(' ');
        return words.length > 200 ? words.slice(0, 200).join(' ') + '...' : textContent;
      case 'balanced':
      default:
        const balancedWords = textContent.split(' ');
        return balancedWords.length > 100 ? balancedWords.slice(0, 100).join(' ') + '...' : textContent;
    }
  }, [textContent, balanceConfig.textSize]);

  // Mock chart data if none provided
  const defaultChartData: ChartData[] = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 600 },
    { name: 'Apr', value: 800 },
    { name: 'May', value: 700 },
    { name: 'Jun', value: 900 }
  ];

  const effectiveChartData = chartData.length > 0 ? chartData : defaultChartData;
  const preferenceViz = getPreferenceVisualization();

  return (
    <div className={`advanced-preference-balance w-full space-y-4 ${className}`}>
      {/* Header with preference indicator */}
      <Card className="border-2 border-gray-200 shadow-lg">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-[#4B9770]" />
              {title}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={preferenceViz.color} className="flex items-center gap-1">
                {preferenceViz.icon}
                {preferenceViz.label}
              </Badge>
              {showControls && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsInteractive(!isInteractive)}
                  className="text-gray-600 hover:text-[#4B9770]"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
          
          {preferences.reasoning && (
            <p className="text-sm text-gray-600 mt-2 italic">
              🧠 AI Reasoning: {preferences.reasoning}
            </p>
          )}
        </CardHeader>

        {/* Interactive Controls */}
        {isInteractive && showControls && (
          <CardContent className="border-t bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-3">
              <div>
                <label className="block text-sm font-medium mb-2">Chart Type</label>
                <div className="flex gap-2">
                  {(['line', 'bar', 'area', 'pie'] as const).map((type) => (
                    <Button
                      key={type}
                      variant={chartType === type ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setChartType(type)}
                      className="capitalize"
                    >
                      {type}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Manual Override</label>
                <Button
                  variant={manualOverride ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setManualOverride(!manualOverride)}
                  className="w-full"
                >
                  {manualOverride ? <Eye className="w-4 h-4 mr-2" /> : <EyeOff className="w-4 h-4 mr-2" />}
                  {manualOverride ? 'Manual' : 'Auto'}
                </Button>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Preference Override</label>
                <div className="flex gap-1">
                  {(['visual', 'text', 'mixed'] as const).map((pref) => (
                    <Button
                      key={pref}
                      variant="outline"
                      size="sm"
                      onClick={() => onPreferenceOverride?.({
                        ...preferences,
                        preference: pref,
                        confidence: 0.9,
                        reasoning: `Manually set to ${pref} preference`
                      })}
                      className="text-xs"
                    >
                      {pref}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main Content Area */}
      <div className={`grid gap-4 ${
        balanceConfig.layout === 'side-by-side' ? 'md:grid-cols-2' :
        balanceConfig.layout === 'visual-first' ? 'grid-cols-1' :
        balanceConfig.layout === 'text-first' ? 'grid-cols-1' :
        'grid-cols-1'
      }`}>
        
        {/* Chart Section */}
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
                <Badge variant="success" className="ml-2">
                  <Target className="w-3 h-3 mr-1" />
                  Primary Focus
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <MultiTypeChart 
              data={effectiveChartData}
              type={chartType}
              size={balanceConfig.chartSize}
            />
          </CardContent>
        </Card>

        {/* Text Section */}
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
                <Badge variant="default" className="ml-2">
                  <Target className="w-3 h-3 mr-1" />
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
                  onClick={() => {
                    setCurrentConfig({
                      ...balanceConfig,
                      textSize: 'detailed'
                    });
                    setManualOverride(true);
                  }}
                >
                  <Maximize2 className="w-4 h-4 mr-2" />
                  Show More Details
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Configuration Debug Panel (Development Only) */}
      {process.env.NODE_ENV === 'development' && (
        <Card className="border-dashed border-gray-300 bg-gray-50">
          <CardContent className="pt-4">
            <div className="text-xs font-mono text-gray-600 space-y-1">
              <div><strong>Layout:</strong> {balanceConfig.layout}</div>
              <div><strong>Chart Size:</strong> {balanceConfig.chartSize}</div>
              <div><strong>Text Size:</strong> {balanceConfig.textSize}</div>
              <div><strong>Emphasis:</strong> {balanceConfig.emphasis}</div>
              <div><strong>Confidence:</strong> {(preferences.confidence * 100).toFixed(1)}%</div>
              <div><strong>Keywords:</strong> {preferences.keywords_found.join(', ')}</div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedPreferenceBalance;
export type { PreferenceData, BalanceConfig, ChartData };