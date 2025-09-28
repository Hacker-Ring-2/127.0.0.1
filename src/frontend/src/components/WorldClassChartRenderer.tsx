/**
 * 🚀 WORLD-CLASS CHART RENDERER
 * 
 * This component renders beautiful, interactive financial visualizations
 * created by our revolutionary visualization engine
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, BarChart3, TrendingUp, Activity } from 'lucide-react';

// Plotly type declaration
declare global {
  interface Window {
    Plotly?: {
      newPlot: (container: HTMLElement, data: unknown, layout: unknown, config?: unknown) => void;
    };
  }
}

interface ChartData {
  type: string;
  title: string;
  html_content?: string;
  base64_data?: string;
  insights: string[];
}

interface WorldClassChartProps {
  chartData: {
    status: string;
    visualization_engine?: string;
    chart_count: number;
    charts: ChartData[];
    insights?: string[];
    generation_method?: string;
  };
}

const WorldClassChartRenderer: React.FC<WorldClassChartProps> = ({ chartData }) => {
  const [activeTab, setActiveTab] = useState('0');
  const chartRefs = useRef<(HTMLDivElement | null)[]>([]);

  const renderCharts = useCallback(() => {
    console.log('Rendering charts:', chartData.charts?.length);
    
    chartData.charts.forEach((chart, index) => {
      const chartContainer = chartRefs.current[index];
      if (chartContainer && chart.html_content) {
        console.log(`Rendering chart ${index}:`, chart.type);
        
        try {
          // Clear container first
          chartContainer.innerHTML = '';
          
          // Method 1: Try to extract and use Plotly configuration
          const plotlyConfig = extractPlotlyConfig(chart.html_content);
          if (plotlyConfig && window.Plotly) {
            console.log(`Using extracted Plotly config for chart ${index}`);
            window.Plotly.newPlot(
              chartContainer, 
              plotlyConfig.data, 
              plotlyConfig.layout,
              { 
                responsive: true, 
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
              }
            );
            
            // Verify chart rendered
            setTimeout(() => {
              const plotlyDiv = chartContainer.querySelector('.plotly-graph-div');
              if (plotlyDiv) {
                console.log(`✅ Chart ${index} rendered successfully with Plotly`);
              } else {
                console.warn(`⚠️ Chart ${index} may not have rendered properly`);
              }
            }, 100);
            
          } else {
            // Method 2: Fallback to direct HTML injection
            console.log(`Using direct HTML injection for chart ${index}`);
            chartContainer.innerHTML = chart.html_content;
            
            // Try to execute any scripts in the HTML
            const scripts = chartContainer.querySelectorAll('script');
            scripts.forEach(script => {
              const newScript = document.createElement('script');
              newScript.textContent = script.textContent;
              document.head.appendChild(newScript);
            });
            
            console.log(`✅ Chart ${index} rendered with HTML injection`);
          }
          
        } catch (error) {
          console.error(`❌ Error rendering chart ${index}:`, error);
          chartContainer.innerHTML = `
            <div class="flex items-center justify-center h-64 text-red-500 bg-red-50 rounded-lg border border-red-200">
              <div class="text-center p-4">
                <AlertCircle className="h-8 w-8 mx-auto mb-2" />
                <p class="font-semibold">Error rendering chart ${index + 1}</p>
                <p class="text-sm mt-1">Chart type: ${chart.type}</p>
                <p class="text-xs mt-2 text-red-600">${error.message}</p>
              </div>
            </div>
          `;
        }
      } else {
        console.warn(`Chart container or content missing for chart ${index}`);
      }
    });
  }, [chartData.charts]);

  useEffect(() => {
    if (chartData.status === 'success' && chartData.charts) {
      console.log('🔄 Chart data updated, preparing to render...');
      console.log('Chart data summary:', {
        total: chartData.charts.length,
        types: chartData.charts.map(c => c.type),
        hasContent: chartData.charts.map(c => !!c.html_content),
        contentLengths: chartData.charts.map(c => c.html_content?.length || 0)
      });
      
      // Enhanced Plotly loading with better error handling
      if (!window.Plotly) {
        console.log('Loading Plotly.js...');
        const script = document.createElement('script');
        script.src = 'https://cdn.plot.ly/plotly-2.26.0.min.js';
        script.onload = () => {
          console.log('✅ Plotly.js loaded successfully');
          setTimeout(() => renderCharts(), 100); // Small delay to ensure DOM is ready
        };
        script.onerror = (error) => {
          console.error('❌ Failed to load Plotly.js:', error);
        };
        document.head.appendChild(script);
      } else {
        console.log('✅ Plotly.js already available');
        setTimeout(() => renderCharts(), 100); // Small delay to ensure DOM is ready
      }
    } else {
      console.log('⏳ Waiting for chart data:', {
        status: chartData.status,
        hasCharts: !!chartData.charts?.length,
        chartCount: chartData.charts?.length || 0
      });
    }
  }, [chartData, renderCharts]);

  const extractPlotlyConfig = (htmlContent: string) => {
    try {
      // Enhanced Plotly configuration extraction
      console.log('Extracting Plotly config from HTML...');
      
      // Method 1: Try to extract from variable declarations (most reliable for generated HTML)
      const dataVarMatch = htmlContent.match(/var\s+data\s*=\s*(\[[\s\S]*?\]);/);
      const layoutVarMatch = htmlContent.match(/var\s+layout\s*=\s*(\{[\s\S]*?\});/);
      
      if (dataVarMatch && layoutVarMatch) {
        console.log('Found variable declarations');
        try {
          // Use Function constructor for safe evaluation of JavaScript objects
          const dataStr = dataVarMatch[1].trim();
          const layoutStr = layoutVarMatch[1].trim();
          
          console.log('Evaluating data configuration...');
          const data = new Function('return ' + dataStr)();
          
          console.log('Evaluating layout configuration...');
          const layout = new Function('return ' + layoutStr)();
          
          console.log('Successfully extracted Plotly config:', { 
            dataLength: data.length, 
            layoutKeys: Object.keys(layout) 
          });
          
          return { data, layout };
        } catch (evalError) {
          console.error('JavaScript evaluation error:', evalError);
        }
      }
      
      // Method 2: Try to extract from Plotly.newPlot call with JSON data
      const newPlotMatch = htmlContent.match(/Plotly\.newPlot\(\s*[^,]+,\s*(\[[\s\S]*?\]),\s*(\{[\s\S]*?\})/);
      if (newPlotMatch) {
        console.log('Found Plotly.newPlot configuration');
        try {
          const data = JSON.parse(newPlotMatch[1]);
          const layout = JSON.parse(newPlotMatch[2]);
          console.log('Successfully parsed JSON Plotly config:', { dataLength: data.length, layoutKeys: Object.keys(layout) });
          return { data, layout };
        } catch (parseError) {
          console.error('JSON parsing error:', parseError);
        }
      }
      
      // Method 3: Try to extract from "data": patterns in embedded JSON
      const dataMatch = htmlContent.match(/"data":\s*(\[[\s\S]*?\])/);
      const layoutMatch = htmlContent.match(/"layout":\s*(\{[\s\S]*?\})/);
      
      if (dataMatch && layoutMatch) {
        console.log('Found data/layout pattern');
        try {
          const data = JSON.parse(dataMatch[1]);
          const layout = JSON.parse(layoutMatch[1]);
          return { data, layout };
        } catch (parseError) {
          console.error('Alternative parsing error:', parseError);
        }
      }
      
      console.warn('Could not extract Plotly configuration, falling back to HTML injection');
      return null;
    } catch (error) {
      console.error('Failed to extract Plotly config:', error);
      return null;
    }
  };

  const getChartIcon = (type: string) => {
    switch (type) {
      case 'candlestick':
      case 'ohlc':
        return <TrendingUp className="h-4 w-4" />;
      case 'timeseries':
      case 'line':
        return <Activity className="h-4 w-4" />;
      case 'volume_analysis':
      case 'bar':
        return <BarChart3 className="h-4 w-4" />;
      default:
        return <BarChart3 className="h-4 w-4" />;
    }
  };

  const getChartTypeColor = (type: string) => {
    switch (type) {
      case 'candlestick':
      case 'ohlc':
        return 'bg-green-100 text-green-800';
      case 'timeseries':
        return 'bg-blue-100 text-blue-800';
      case 'volume_analysis':
        return 'bg-purple-100 text-purple-800';
      case 'correlation':
        return 'bg-orange-100 text-orange-800';
      case 'distribution':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (chartData.status !== 'success' || !chartData.charts || chartData.charts.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center text-gray-500">
            <AlertCircle className="h-8 w-8 mx-auto mb-2" />
            <p>No charts generated</p>
            <p className="text-sm">Please provide valid financial data</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* Header with insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            World-Class Financial Visualization
            {chartData.visualization_engine && (
              <Badge variant="secondary" className="ml-2">
                {chartData.visualization_engine}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{chartData.chart_count}</div>
              <div className="text-sm text-gray-600">Charts Generated</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">✨</div>
              <div className="text-sm text-gray-600">Professional Quality</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">🎯</div>
              <div className="text-sm text-gray-600">AI-Powered Analysis</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">📊</div>
              <div className="text-sm text-gray-600">Interactive Charts</div>
            </div>
          </div>
          
          {chartData.insights && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">📈 Data Insights</h4>
              <ul className="space-y-1">
                {chartData.insights.map((insight, index) => (
                  <li key={index} className="text-sm text-blue-800 flex items-start gap-2">
                    <span className="text-blue-600">•</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charts */}
      {chartData.charts.length === 1 ? (
        // Single chart - full width
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getChartIcon(chartData.charts[0].type)}
              {chartData.charts[0].title}
              <Badge className={getChartTypeColor(chartData.charts[0].type)}>
                {chartData.charts[0].type}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div 
              ref={(el) => { chartRefs.current[0] = el; }}
              className="w-full h-[600px] mb-4"
            />
            {chartData.charts[0].insights && (
              <div className="bg-gray-50 p-3 rounded">
                <h5 className="font-medium text-gray-800 mb-2">Chart Insights</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  {chartData.charts[0].insights.map((insight, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span>•</span> {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        // Multiple charts - tabbed interface
        <Card>
          <CardHeader>
            <CardTitle>📊 Interactive Chart Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-auto gap-1 mb-4">
                {chartData.charts.map((chart, index) => (
                  <TabsTrigger 
                    key={index} 
                    value={index.toString()}
                    className="flex items-center gap-2"
                  >
                    {getChartIcon(chart.type)}
                    <span className="hidden md:inline">{chart.title.split(' ')[0]}</span>
                    <Badge 
                      className={getChartTypeColor(chart.type)}
                    >
                      {chart.type}
                    </Badge>
                  </TabsTrigger>
                ))}
              </TabsList>

              {chartData.charts.map((chart, index) => (
                <TabsContent key={index} value={index.toString()}>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      {getChartIcon(chart.type)}
                      <h3 className="text-lg font-semibold">{chart.title}</h3>
                    </div>
                    
                    <div 
                      ref={(el) => { chartRefs.current[index] = el; }}
                      className="w-full h-[600px] mb-4 border rounded-lg"
                    />
                    
                    {chart.insights && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
                          <Activity className="h-4 w-4" />
                          Chart Insights
                        </h5>
                        <ul className="text-sm text-gray-600 space-y-2">
                          {chart.insights.map((insight, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-blue-500 font-bold">•</span> 
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default WorldClassChartRenderer;