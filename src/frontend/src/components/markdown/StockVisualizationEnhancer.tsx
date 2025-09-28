'use client';
import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, Activity, AlertTriangle, Target, Award } from 'lucide-react';

interface ChartDataPoint {
  legend_label: string;
  x_axis_data: (string | number)[];
  y_axis_data: number[];
  color: string;
}

interface ChartData {
  chart_type: string;
  chart_title: string;
  x_label: string;
  y_label: string;
  data: ChartDataPoint[];
}

interface StockVisualizationEnhancerProps {
  chartTitle: string;
  chartData: ChartData | null;
  children: React.ReactNode;
}

const StockVisualizationEnhancer: React.FC<StockVisualizationEnhancerProps> = ({
  chartTitle,
  chartData,
  children
}) => {
  // Detect if this is stock/financial data
  const isStockData = useMemo(() => {
    const title = chartTitle.toLowerCase();
    const indicators = ['stock', 'price', 'volume', 'trading', 'ohlc', 'market', 'financial'];
    return indicators.some(indicator => title.includes(indicator));
  }, [chartTitle]);

  // Analyze data for trend indicators
  const analysisMetrics = useMemo(() => {
    if (!isStockData || !chartData?.data) return null;

    try {
      const data = chartData.data[0];
      if (!data?.y_axis_data || data.y_axis_data.length < 2) return null;

      const values = data.y_axis_data.filter((val: unknown) => typeof val === 'number') as number[];
      if (values.length < 2) return null;

      const latest = values[values.length - 1];
      const previous = values[values.length - 2];
      const first = values[0];

      const dailyChange = latest - previous;
      const dailyChangePercent = (dailyChange / previous) * 100;
      const overallChange = latest - first;
      const overallChangePercent = (overallChange / first) * 100;

      const max = Math.max(...values);
      const min = Math.min(...values);
      const avg = values.reduce((sum: number, val: number) => sum + val, 0) / values.length;
      const volatility = Math.sqrt(values.reduce((sum: number, val: number) => sum + Math.pow(val - avg, 2), 0) / values.length);

      return {
        latest,
        dailyChange,
        dailyChangePercent,
        overallChange,
        overallChangePercent,
        max,
        min,
        avg,
        volatility,
        trend: dailyChange > 0 ? 'up' : dailyChange < 0 ? 'down' : 'stable'
      };
    } catch (error) {
      console.warn('Failed to analyze chart data:', error);
      return null;
    }
  }, [isStockData, chartData]);

  const formatNumber = (num: number) => {
    if (Math.abs(num) >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (Math.abs(num) >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (Math.abs(num) >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  const formatPercent = (num: number) => {
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
  };

  if (!isStockData) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {/* Enhanced Chart Container */}
      <div className="relative bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        
        {/* Stock Performance Header */}
        {analysisMetrics && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {analysisMetrics.trend === 'up' ? (
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  ) : analysisMetrics.trend === 'down' ? (
                    <TrendingDown className="w-5 h-5 text-red-600" />
                  ) : (
                    <Activity className="w-5 h-5 text-gray-600" />
                  )}
                  <span className="text-lg font-semibold text-gray-800">
                    {formatNumber(analysisMetrics.latest)}
                  </span>
                </div>
                
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  analysisMetrics.dailyChange >= 0
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {formatPercent(analysisMetrics.dailyChangePercent)}
                </div>
              </div>

              {/* Performance Badges */}
              <div className="flex items-center space-x-2">
                {analysisMetrics.volatility > analysisMetrics.avg * 0.1 && (
                  <div className="flex items-center space-x-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-md text-xs">
                    <AlertTriangle className="w-3 h-3" />
                    <span>High Volatility</span>
                  </div>
                )}
                
                {analysisMetrics.overallChangePercent > 10 && (
                  <div className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-800 rounded-md text-xs">
                    <Award className="w-3 h-3" />
                    <span>Strong Growth</span>
                  </div>
                )}

                {analysisMetrics.latest > analysisMetrics.avg && (
                  <div className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-xs">
                    <Target className="w-3 h-3" />
                    <span>Above Average</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Main Chart */}
        <div className="p-6">
          {children}
        </div>

        {/* Stock Metrics Footer */}
        {analysisMetrics && (
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-100">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500 block">High</span>
                <span className="font-medium text-gray-900">{formatNumber(analysisMetrics.max)}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Low</span>
                <span className="font-medium text-gray-900">{formatNumber(analysisMetrics.min)}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Average</span>
                <span className="font-medium text-gray-900">{formatNumber(analysisMetrics.avg)}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Overall Change</span>
                <span className={`font-medium ${
                  analysisMetrics.overallChange >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercent(analysisMetrics.overallChangePercent)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Market Intelligence Insights */}
      {analysisMetrics && (
        <div className="mt-4 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 rounded-lg p-4 border border-indigo-100">
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
            <Activity className="w-4 h-4 mr-2" />
            Market Intelligence Insights
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center space-x-2">
              <span className="text-orange-600">🔥</span>
              <span>
                <strong>Momentum:</strong> {
                  analysisMetrics.dailyChangePercent > 2 ? 'Strong Bullish' :
                  analysisMetrics.dailyChangePercent > 0 ? 'Moderate Bullish' :
                  analysisMetrics.dailyChangePercent < -2 ? 'Strong Bearish' : 'Moderate Bearish'
                }
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-yellow-600">⚠️</span>
              <span>
                <strong>Risk Level:</strong> {
                  analysisMetrics.volatility > analysisMetrics.avg * 0.15 ? 'High' :
                  analysisMetrics.volatility > analysisMetrics.avg * 0.08 ? 'Moderate' : 'Low'
                }
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-green-600">🎯</span>
              <span>
                <strong>Position:</strong> {
                  analysisMetrics.latest > analysisMetrics.avg * 1.1 ? 'Above Fair Value' :
                  analysisMetrics.latest < analysisMetrics.avg * 0.9 ? 'Below Fair Value' : 'Fair Value Range'
                }
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-blue-600">🌐</span>
              <span>
                <strong>Trend:</strong> {
                  analysisMetrics.overallChangePercent > 5 ? 'Strong Uptrend' :
                  analysisMetrics.overallChangePercent > 0 ? 'Uptrend' :
                  analysisMetrics.overallChangePercent < -5 ? 'Strong Downtrend' : 'Downtrend'
                }
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockVisualizationEnhancer;