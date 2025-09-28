'use client';

import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { useIsMobile } from '@/hooks/use-is-mobile';

interface StockData {
  date: string;
  open: string | number;
  high: string | number;
  low: string | number;
  close: string | number;
  volume: string | number;
  timestamp?: string;
}

interface StockChartProps {
  data: StockData[];
  isPositive: boolean;
  loading: boolean;
  symbol: string;
  period: string;
  isModalView: boolean;
  heightOfStockChart: string;
}

interface ChartDimensions {
  width: number;
  height: number;
  isReady: boolean;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: {
      high: number;
      low: number;
      open: number;
      close: number;
      volume: number;
    };
  }>;
  label?: string;
  symbol?: string;
}

const CustomTooltip = ({ active, payload, label, symbol }: TooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 border rounded-md border-gray-200 shadow-md text-sm">
        <p className="font-medium">{symbol}</p>
        <p className="text-gray-700 text-xs font-semibold">
          High: {`${Number(payload[0].payload.high).toFixed(2)}`}
        </p>
        <p className="text-gray-700 text-xs font-semibold">
          Low: {`${Number(payload[0].payload.low).toFixed(2)}`}
        </p>
        <p className="text-gray-700 text-xs font-semibold">
          Open: {`${Number(payload[0].payload.open).toFixed(2)}`}
        </p>
        <p className="text-gray-700 text-xs font-semibold">
          Close: {`${Number(payload[0].payload.close).toFixed(2)}`}
        </p>
        <p className="text-gray-600 text-xs">{label}</p>
      </div>
    );
  }
  return null;
};

const EnhancedChartSkeleton = () => {
  return (
    <div className="h-full w-full p-4 space-y-4 animate-pulse bg-[var(--primary-text-bg)] rounded-md">
      <div className="flex items-center justify-center h-full text-gray-500">Loading chart...</div>
    </div>
  );
};

const ChartLoadingFallback = ({ message = 'Preparing chart...' }: { message?: string }) => {
  return (
    <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded-md">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
        <p className="text-gray-600 text-sm">{message}</p>
      </div>
    </div>
  );
};

const StockChart: React.FC<StockChartProps> = ({
  data,
  isPositive,
  loading,
  symbol,
  period,
  isModalView,
  heightOfStockChart,
}) => {
  const isMobile = useIsMobile();
  const containerRef = useRef<HTMLDivElement>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [dimensions, setDimensions] = useState<ChartDimensions>({
    width: 0,
    height: 0,
    isReady: false,
  });

  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 5;

  const chartColor = isPositive ? '#22c55e' : '#ef4444';

  // Update dimensions with retry logic
  const updateDimensions = useCallback(() => {
    if (!containerRef.current) {
      if (retryCount < maxRetries) {
        timeoutRef.current = setTimeout(() => {
          setRetryCount((prev) => prev + 1);
        }, 100);
      }
      return;
    }

    const rect = containerRef.current.getBoundingClientRect();
    const width = containerRef.current.offsetWidth || rect.width;
    const height = containerRef.current.offsetHeight || rect.height;

    // Consider dimensions ready if both width and height are greater than 0
    const isReady = width > 0 && height > 0;

    setDimensions((prev) => {
      // Only update if dimensions actually changed or readiness changed
      if (prev.width !== width || prev.height !== height || prev.isReady !== isReady) {
        return { width, height, isReady };
      }
      return prev;
    });

    // Reset retry count on successful dimension detection
    if (isReady) {
      setRetryCount(0);
    }
  }, [retryCount, maxRetries]);

  // Set up ResizeObserver and initial dimension detection
  useEffect(() => {
    if (!containerRef.current) return;

    // Initial dimension check
    updateDimensions();

    // Set up ResizeObserver for dynamic dimension changes
    resizeObserverRef.current = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) {
          setDimensions({ width, height, isReady: true });
          setRetryCount(0);
        }
      }
    });

    resizeObserverRef.current.observe(containerRef.current);

    // Fallback timeout for initial render
    timeoutRef.current = setTimeout(updateDimensions, 50);

    return () => {
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect();
        resizeObserverRef.current = null;
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [updateDimensions]);

  // Retry mechanism for dimension detection
  useEffect(() => {
    if (!dimensions.isReady && retryCount > 0 && retryCount <= maxRetries) {
      timeoutRef.current = setTimeout(updateDimensions, 100 * retryCount);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [retryCount, dimensions.isReady, updateDimensions, maxRetries]);

  const chartData = useMemo(() => {
    return data.map((item) => ({
      date: typeof item.timestamp === 'string' ? item.timestamp : item.date,
      value: typeof item.close === 'string' ? parseFloat(item.close.replace(/,/g, '')) : item.close,
      close: typeof item.close === 'string' ? parseFloat(item.close.replace(/,/g, '')) : item.close,
      open: typeof item.open === 'string' ? parseFloat(item.open.replace(/,/g, '')) : item.open,
      high: typeof item.high === 'string' ? parseFloat(item.high.replace(/,/g, '')) : item.high,
      low: typeof item.low === 'string' ? parseFloat(item.low.replace(/,/g, '')) : item.low,
      volume:
        typeof item.volume === 'string' ? parseFloat(item.volume.replace(/,/g, '')) : item.volume,
    }));
  }, [data]);

  const maxValue = useMemo(() => {
    if (chartData.length === 0) return 0;
    const max = Math.max(...chartData.map((item) => item.value));
    return max < 10
      ? parseFloat((Math.ceil((max + 0.0005) * 1000) / 1000).toFixed(3))
      : parseFloat((Math.ceil((max + 0.005) * 100) / 100).toFixed(2));
  }, [chartData]);

  const minValue = useMemo(() => {
    if (chartData.length === 0) return 0;
    const min = Math.min(...chartData.map((item) => item.value));
    return maxValue < 10
      ? parseFloat((Math.floor(min * 1000) / 1000).toFixed(3))
      : parseFloat((Math.floor(min * 100) / 100).toFixed(2));
  }, [chartData, maxValue]);

  const yAxisTicks = useMemo(() => {
    if (maxValue === minValue) return [minValue];
    const isSmallRange = maxValue < 10;
    const stepSize = (maxValue - minValue) / 4;

    return Array.from({ length: 5 }, (_, i) =>
      parseFloat((minValue + i * stepSize).toFixed(isSmallRange ? 3 : 2))
    );
  }, [minValue, maxValue]);

  const xAxisTicks = useMemo(() => {
    const dataLength = chartData.length;
    if (dataLength === 0) return [];

    // Special handling for 1MO period in modal view (show 10 ticks)
    if (isModalView && period === '1M') {
      const ticks = [];
      const targetTickCount = 10;
      const step = Math.max(1, Math.floor(dataLength / (targetTickCount - 1)));

      for (let i = 0; i < dataLength; i += step) {
        if (ticks.length < targetTickCount) {
          ticks.push(i);
        }
      }

      if (ticks[ticks.length - 1] !== dataLength - 1) {
        ticks.push(dataLength - 1);
      }

      while (ticks.length < targetTickCount && ticks.length < dataLength) {
        const lastTick: number = ticks[ticks.length - 1];
        ticks.push(Math.min(lastTick + 1, dataLength - 1));
      }

      return ticks;
    }

    if (isModalView && period === '3M') {
      const targetTickCount = 10;
      const ticks = [];
      const firstDate = new Date(chartData[0]?.date);
      const lastDate = new Date(chartData[dataLength - 1]?.date);
      const totalDays = Math.floor(
        (lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)
      );
      const approxDayStep = Math.floor(totalDays / (targetTickCount - 1));

      ticks.push(0);

      for (let i = 1; i < targetTickCount - 1; i++) {
        const targetDate = new Date(firstDate);
        targetDate.setDate(firstDate.getDate() + i * approxDayStep);

        const tickIndex = chartData.findIndex((item) => {
          const itemDate = new Date(item.date);
          return itemDate >= targetDate;
        });

        if (tickIndex !== -1 && !ticks.includes(tickIndex)) {
          ticks.push(tickIndex);
        }
      }

      if (!ticks.includes(dataLength - 1)) {
        ticks.push(dataLength - 1);
      }

      return Array.from(new Set(ticks)).sort((a, b) => a - b);
    }

    if (isModalView && period === '6M') {
      const lastDate = new Date(chartData[chartData.length - 1]?.date);
      const firstDate = new Date(lastDate);
      firstDate.setMonth(firstDate.getMonth() - 6);

      const boundaryIndices = [0, chartData.length - 1];
      const idealIntervalDays = Math.floor(180 / 10);
      const idealDates = [];
      const currentDate = new Date(firstDate);

      while (currentDate <= lastDate) {
        idealDates.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + idealIntervalDays);
      }

      const availableDates = chartData.map((item) => new Date(item.date).getTime());
      const tickIndices = [...boundaryIndices];

      idealDates.forEach((idealDate) => {
        const idealTime = idealDate.getTime();
        const closestIndex = availableDates.reduce((prev, curr, index) => {
          const currDiff = Math.abs(curr - idealTime);
          const prevDiff = Math.abs(availableDates[prev] - idealTime);
          return currDiff < prevDiff ? index : prev;
        }, 0);

        if (!tickIndices.includes(closestIndex)) {
          tickIndices.push(closestIndex);
        }
      });

      tickIndices.sort((a, b) => a - b);

      if (tickIndices[tickIndices.length - 1] !== chartData.length - 1) {
        tickIndices.push(chartData.length - 1);
      }

      return tickIndices.slice(0, 12);
    }

    if (isModalView && period === 'YTD') {
      const lastDate = new Date(chartData[chartData.length - 1]?.date);
      const currentYear = lastDate.getFullYear();
      const currentMonth = lastDate.getMonth();
      const monthIndices = [];
      const seenMonths = new Set();

      for (let i = 0; i < chartData.length; i++) {
        const date = new Date(chartData[i].date);
        const year = date.getFullYear();
        const month = date.getMonth();

        if (year === currentYear && month <= currentMonth && !seenMonths.has(month)) {
          seenMonths.add(month);
          monthIndices.push(i);
        }
      }

      const lastIndex = chartData.length - 1;
      const lastPointMonth = new Date(chartData[lastIndex].date).getMonth();
      const lastPointIncluded = monthIndices.some((index) => {
        return new Date(chartData[index].date).getMonth() === lastPointMonth;
      });

      if (!lastPointIncluded) {
        monthIndices.push(lastIndex);
      }

      return monthIndices.sort((a, b) => a - b);
    }

    if (isModalView && period === '1Y') {
      const lastIndex = chartData.length - 1;
      const lastDate = new Date(chartData[lastIndex]?.date);
      const firstDate = new Date(lastDate);
      firstDate.setFullYear(firstDate.getFullYear() - 1);

      const currentMonth = lastDate.getMonth();
      const currentYear = lastDate.getFullYear();
      const monthMap = new Map();

      chartData.forEach((item, index) => {
        const date = new Date(item.date);

        if (date >= firstDate && date <= lastDate) {
          const month = date.getMonth();
          const year = date.getFullYear();

          if (month === currentMonth && year === currentYear) return;

          const key = `${year}-${month}`;
          if (!monthMap.has(key)) {
            monthMap.set(key, index);
          }
        }
      });

      const monthIndices = Array.from(monthMap.values());

      if (monthIndices[0] !== 0) monthIndices.unshift(0);
      if (monthIndices[monthIndices.length - 1] !== lastIndex) {
        monthIndices.push(lastIndex);
      }

      return monthIndices.sort((a, b) => a - b);
    }

    if (isModalView && period === '5Y') {
      const lastIndex = chartData.length - 1;
      const lastDate = new Date(chartData[lastIndex]?.date);
      const startDate = new Date(lastDate);
      startDate.setFullYear(startDate.getFullYear() - 5);

      const startMonth = startDate.getMonth();
      const adjustedStartMonth = startMonth >= 6 ? 6 : 0;
      startDate.setMonth(adjustedStartMonth);
      startDate.setDate(1);

      const tickDates: string[] = [];
      const temp = new Date(startDate);

      while (temp <= lastDate) {
        tickDates.push(temp.toISOString().split('T')[0]);
        temp.setMonth(temp.getMonth() + 6);
      }

      tickDates.unshift(chartData[0].date);
      tickDates.push(chartData[lastIndex].date);

      const tickIndices = tickDates
        .map((tickDate) => {
          const tick = new Date(tickDate);
          return chartData.findIndex((d) => {
            const date = new Date(d.date);
            return date.getFullYear() === tick.getFullYear() && date.getMonth() === tick.getMonth();
          });
        })
        .filter((index) => index !== -1);

      return Array.from(new Set(tickIndices)).sort((a, b) => a - b);
    }

    if (isModalView && period === 'MAX') {
      const years = new Set<number>();
      chartData.forEach((item) => {
        const year = new Date(item.date).getFullYear();
        years.add(year);
      });

      const uniqueYears = Array.from(years).sort((a, b) => a - b);
      const totalYears = uniqueYears.length;
      const lastIndex = chartData.length - 1;
      const lastDate = new Date(chartData[lastIndex].date);
      const lastYear = lastDate.getFullYear();

      if (totalYears <= 12) {
        const yearIndices = uniqueYears.map((year) => {
          return chartData.findIndex((item) => new Date(item.date).getFullYear() === year);
        });

        if (!yearIndices.includes(0)) {
          yearIndices.unshift(0);
        }

        const hasCurrentYear = yearIndices.some(
          (index) => new Date(chartData[index].date).getFullYear() === lastYear
        );

        const alreadyAtLastIndex = yearIndices.includes(lastIndex);

        if (!alreadyAtLastIndex) {
          if (!hasCurrentYear) {
            yearIndices.push(lastIndex);
          } else {
            const idxToReplace = yearIndices.findIndex(
              (index) => new Date(chartData[index].date).getFullYear() === lastYear
            );
            if (idxToReplace !== -1) {
              yearIndices[idxToReplace] = lastIndex;
            }
          }
        }

        return yearIndices.sort((a, b) => a - b);
      }

      const targetTickCount = 12;
      const step = totalYears / (targetTickCount - 1);
      const selectedYears = new Set<number>();

      selectedYears.add(uniqueYears[0]);
      selectedYears.add(uniqueYears[uniqueYears.length - 1]);

      for (let i = 1; i < targetTickCount - 1; i++) {
        const yearIndex = Math.round(i * step);
        if (yearIndex < uniqueYears.length) {
          selectedYears.add(uniqueYears[yearIndex]);
        }
      }

      const yearIndices = Array.from(selectedYears)
        .map((year) => {
          return chartData.findIndex((item) => new Date(item.date).getFullYear() === year);
        })
        .filter((index) => index !== -1);

      if (!yearIndices.includes(0)) yearIndices.unshift(0);
      if (!yearIndices.includes(lastIndex)) yearIndices.push(lastIndex);

      return yearIndices.sort((a, b) => a - b);
    }

    // Default case for non-modal view
    const tickCount = isMobile ? 3 : 5;
    const step = Math.floor(dataLength / (tickCount - 1));
    const ticks = [];

    for (let i = 0; i < tickCount; i++) {
      const index = i * step;
      if (index < dataLength) {
        ticks.push(index);
      }
    }

    if (ticks.length > 0 && ticks[ticks.length - 1] !== dataLength - 1) {
      ticks.push(dataLength - 1);
    }

    return ticks;
  }, [chartData, isMobile, period, isModalView]);

  const gradientId = useMemo(() => {
    return `areaGradient-${isPositive ? 'positive' : 'negative'}`;
  }, [isPositive]);

  // Show loading skeleton if data is loading
  if (loading) {
    return (
      <div
        className="chart-container"
        style={{
          width: '100%',
          height: heightOfStockChart,
          minHeight: heightOfStockChart,
        }}
      >
        <EnhancedChartSkeleton />
      </div>
    );
  }

  // Show loading fallback if dimensions aren't ready yet
  if (!dimensions.isReady && retryCount <= maxRetries) {
    return (
      <div
        className="chart-container"
        style={{
          width: '100%',
          height: heightOfStockChart,
          minHeight: heightOfStockChart,
        }}
        ref={containerRef}
      >
        <ChartLoadingFallback
          message={retryCount > 0 ? 'Loading chart...' : 'Preparing chart...'}
        />
      </div>
    );
  }

  // Show error state if we've exceeded max retries and still no dimensions
  if (!dimensions.isReady && retryCount > maxRetries) {
    return (
      <div
        className="chart-container"
        style={{
          width: '100%',
          height: heightOfStockChart,
          minHeight: heightOfStockChart,
        }}
        ref={containerRef}
      >
        <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded-md">
          <div className="text-center">
            <p className="text-red-600 text-sm mb-2">Unable to load chart</p>
            <button
              onClick={() => {
                setRetryCount(0);
                setDimensions({ width: 0, height: 0, isReady: false });
              }}
              className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show message if no data
  if (chartData.length === 0) {
    return (
      <div
        className="chart-container"
        style={{
          width: '100%',
          height: heightOfStockChart,
          minHeight: heightOfStockChart,
        }}
        ref={containerRef}
      >
        <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded-md">
          <p className="text-gray-600 text-sm">No data available</p>
        </div>
      </div>
    );
  }

  // Render the chart when everything is ready
  return (
    <div
      className="chart-container"
      style={{
        width: '100%',
        height: heightOfStockChart,
        minHeight: heightOfStockChart,
        minWidth: '100%',
        display: 'block',
      }}
      ref={containerRef}
    >
      <div className="h-full w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, bottom: 10 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={chartColor} stopOpacity={0.8} />
                <stop offset="100%" stopColor="var(--primary-main-bg)" stopOpacity={0.8} />
              </linearGradient>
            </defs>

            <CartesianGrid vertical={false} horizontal strokeDasharray="3 3" stroke="#E0E0E0" />

            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              ticks={xAxisTicks.map((idx) => chartData[idx]?.date)}
              tick={{ fontSize: 12, fill: '#666' }}
              tickMargin={12}
              tickFormatter={(value) => {
                const date = new Date(value);
                if (period === '5Y') {
                  const month = date.toLocaleDateString('en-US', { month: 'short' });
                  const year = date.getFullYear();
                  return `${month} ${year}`;
                }

                if (period === '1MO' || period === '3MO') {
                  return date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  });
                } else if (['6MO', 'YTD', '1Y'].includes(period)) {
                  return date.toLocaleDateString('en-US', { month: 'short' });
                } else if (['5Y', 'MAX'].includes(period)) {
                  return date.getFullYear().toString();
                }

                return value;
              }}
            />

            <YAxis
              domain={[minValue, maxValue]}
              axisLine={false}
              tickLine={false}
              ticks={yAxisTicks}
              tickFormatter={(value) => `${value}`}
              tick={{ fontSize: 12, fill: '#666' }}
              interval={0}
            />

            <Tooltip content={<CustomTooltip symbol={symbol} />} />

            <Area
              type="monotone"
              dataKey="value"
              fill={`url(#${gradientId})`}
              stroke={chartColor}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default React.memo(StockChart);
