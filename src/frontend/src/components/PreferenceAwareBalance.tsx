/**
 * Preference-Aware Chart/Text Balance Component for TheNZT AI System
 * Implements Step 3: Customize Chart/Text Balance (20 points)
 */

import React, { useEffect, useMemo } from 'react';

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

interface PreferenceBalanceProps {
  preferences: PreferenceData;
  chartContent?: React.ReactNode;
  textContent?: string;
  onBalanceChange?: (config: BalanceConfig) => void;
  className?: string;
}

const PreferenceAwareBalance: React.FC<PreferenceBalanceProps> = ({
  preferences,
  chartContent,
  textContent,
  onBalanceChange,
  className = ""
}) => {
  // Calculate optimal balance based on preferences
  const balanceConfig = useMemo((): BalanceConfig => {
    const { preference, confidence } = preferences;
    
    switch (preference) {
      case 'visual':
        return {
          chartSize: confidence > 0.7 ? 'large' : 'medium',
          textSize: 'brief',
          layout: 'visual-first',
          emphasis: 'charts'
        };
      case 'text':
        return {
          chartSize: 'small',
          textSize: confidence > 0.7 ? 'detailed' : 'balanced',
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

  // Notify parent of balance changes
  useEffect(() => {
    onBalanceChange?.(balanceConfig);
  }, [balanceConfig, onBalanceChange]);

  // Style configurations
  const chartStyles = useMemo(() => {
    const baseStyles = {
      transition: 'all 0.3s ease-in-out',
      borderRadius: '8px',
      overflow: 'hidden'
    };

    switch (balanceConfig.chartSize) {
      case 'large':
        return { ...baseStyles, width: '100%', height: '400px', marginBottom: '1rem' };
      case 'medium':
        return { ...baseStyles, width: '80%', height: '300px', marginBottom: '1rem' };
      case 'small':
        return { ...baseStyles, width: '60%', height: '200px', marginBottom: '0.5rem' };
      default:
        return { ...baseStyles, width: '80%', height: '300px', marginBottom: '1rem' };
    }
  }, [balanceConfig.chartSize]);

  const textStyles = useMemo(() => {
    const baseStyles = {
      transition: 'all 0.3s ease-in-out',
      lineHeight: '1.6',
      color: '#333'
    };

    switch (balanceConfig.textSize) {
      case 'detailed':
        return { ...baseStyles, fontSize: '16px', maxHeight: 'none' };
      case 'balanced':
        return { ...baseStyles, fontSize: '15px', maxHeight: '300px', overflow: 'auto' };
      case 'brief':
        return { ...baseStyles, fontSize: '14px', maxHeight: '150px', overflow: 'hidden' };
      default:
        return { ...baseStyles, fontSize: '15px' };
    }
  }, [balanceConfig.textSize]);

  const containerStyles = useMemo(() => {
    const baseStyles = {
      display: 'flex',
      gap: '1rem',
      padding: '1rem',
      backgroundColor: '#f8f9fa',
      borderRadius: '12px',
      border: '1px solid #e9ecef'
    };

    switch (balanceConfig.layout) {
      case 'visual-first':
        return { ...baseStyles, flexDirection: 'column' as const };
      case 'text-first':
        return { ...baseStyles, flexDirection: 'column-reverse' as const };
      case 'balanced':
        return { ...baseStyles, flexDirection: 'row' as const, flexWrap: 'wrap' as const };
      default:
        return { ...baseStyles, flexDirection: 'column' as const };
    }
  }, [balanceConfig.layout]);

  // Process text content based on preference
  const processedTextContent = useMemo(() => {
    if (!textContent) return '';

    switch (balanceConfig.textSize) {
      case 'brief':
        const sentences = textContent.split('. ');
        return sentences.slice(0, 2).join('. ') + (sentences.length > 2 ? '...' : '');
      case 'detailed':
        return textContent;
      case 'balanced':
      default:
        const words = textContent.split(' ');
        return words.length > 100 ? words.slice(0, 100).join(' ') + '...' : textContent;
    }
  }, [textContent, balanceConfig.textSize]);

  return (
    <div className={`preference-aware-balance ${className}`} style={containerStyles}>
      {/* Preference indicator */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        backgroundColor: preferences.preference === 'visual' ? '#4CAF50' : 
                        preferences.preference === 'text' ? '#2196F3' : '#FF9800',
        color: 'white',
        padding: '4px 8px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 'bold'
      }}>
        {preferences.preference.toUpperCase()} ({(preferences.confidence * 100).toFixed(0)}%)
      </div>

      {/* Chart content */}
      {chartContent && (
        <div 
          className="chart-section" 
          style={{
            ...chartStyles,
            order: balanceConfig.layout === 'text-first' ? 2 : 1,
            flex: balanceConfig.layout === 'balanced' ? '1' : 'none'
          }}
        >
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {chartContent}
          </div>
          
          {balanceConfig.emphasis === 'charts' && (
            <div style={{
              position: 'absolute',
              top: '5px',
              left: '10px',
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '2px 6px',
              borderRadius: '8px',
              fontSize: '10px'
            }}>
              PRIMARY FOCUS
            </div>
          )}
        </div>
      )}

      {/* Text content */}
      {textContent && (
        <div 
          className="text-section" 
          style={{
            ...textStyles,
            order: balanceConfig.layout === 'visual-first' ? 2 : 1,
            flex: balanceConfig.layout === 'balanced' ? '1' : 'none',
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            position: 'relative'
          }}
        >
          {balanceConfig.emphasis === 'text' && (
            <div style={{
              position: 'absolute',
              top: '5px',
              right: '10px',
              backgroundColor: '#2196F3',
              color: 'white',
              padding: '2px 6px',
              borderRadius: '8px',
              fontSize: '10px'
            }}>
              PRIMARY FOCUS
            </div>
          )}
          
          <div dangerouslySetInnerHTML={{ __html: processedTextContent.replace(/\n/g, '<br>') }} />
          
          {balanceConfig.textSize === 'brief' && textContent.length > processedTextContent.length && (
            <button
              style={{
                marginTop: '0.5rem',
                color: '#007bff',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: '12px',
                textDecoration: 'underline'
              }}
              onClick={() => {
                // Could expand text or show modal
                console.log('Expand text requested');
              }}
            >
              Show more details
            </button>
          )}
        </div>
      )}

      {/* Debug info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          position: 'absolute',
          bottom: '10px',
          left: '10px',
          backgroundColor: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '4px 8px',
          borderRadius: '4px',
          fontSize: '10px',
          fontFamily: 'monospace'
        }}>
          Layout: {balanceConfig.layout} | Chart: {balanceConfig.chartSize} | Text: {balanceConfig.textSize}
        </div>
      )}
    </div>
  );
};

export default PreferenceAwareBalance;
export type { PreferenceData, BalanceConfig };