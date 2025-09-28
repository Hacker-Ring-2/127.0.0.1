/**
 * Integration Example: Using PreferenceAwareBalance with TheNZT AI System
 * Shows how to implement Step 3: Customize Chart/Text Balance (20 points)
 */

import React, { useState, useEffect } from 'react';
import PreferenceAwareBalance, { PreferenceData, BalanceConfig } from './PreferenceAwareBalance';

// Mock chart component (replace with actual TheNZT chart components)
interface DataPoint {
  date: string;
  value: number;
}

const MockChart: React.FC<{ data: DataPoint[] }> = ({ data }) => (
  <div style={{
    width: '100%',
    height: '100%',
    background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '18px',
    fontWeight: 'bold'
  }}>
    📊 Financial Chart ({data.length} data points)
  </div>
);

// Example component showing integration
const FinancialAnalysisView: React.FC = () => {
  const [preferences, setPreferences] = useState<PreferenceData>({
    preference: 'mixed',
    confidence: 0.8,
    reasoning: 'User requested both charts and detailed analysis',
    keywords_found: ['chart', 'analysis', 'detailed']
  });

  const [currentBalance, setCurrentBalance] = useState<BalanceConfig | null>(null);

  // Simulate preference detection (in real app, this would come from AI analysis)
  useEffect(() => {
    const simulatePreferenceDetection = () => {
      const scenarios = [
        {
          preference: 'visual' as const,
          confidence: 0.9,
          reasoning: 'User query contained: "show me charts", "visualize", "graph"',
          keywords_found: ['charts', 'visualize', 'graph']
        },
        {
          preference: 'text' as const,
          confidence: 0.85,
          reasoning: 'User query contained: "explain in detail", "analysis", "summary"',
          keywords_found: ['explain', 'detail', 'analysis', 'summary']
        },
        {
          preference: 'mixed' as const,
          confidence: 0.75,
          reasoning: 'User query contained both visual and text indicators',
          keywords_found: ['show', 'explain', 'chart', 'details']
        }
      ];

      const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
      setPreferences(randomScenario);
    };

    // Simulate preference change every 5 seconds for demo
    const interval = setInterval(simulatePreferenceDetection, 5000);
    return () => clearInterval(interval);
  }, []);

  // Mock financial data
  const financialData = [
    { date: '2024-01', value: 100 },
    { date: '2024-02', value: 120 },
    { date: '2024-03', value: 115 },
    { date: '2024-04', value: 135 }
  ];

  const analysisText = `
    Financial Analysis Summary:
    
    The portfolio has shown steady growth over the past quarter with a 35% overall increase.
    Key observations include:
    
    • Strong performance in Q1 2024 with 20% gains
    • Minor correction in March (-4.2%) followed by recovery
    • Current trend indicates continued upward momentum
    • Risk factors include market volatility and sector rotation
    
    Technical indicators suggest a bullish outlook with support levels holding firm.
    The RSI is currently at 68, indicating strong but not overbought conditions.
    
    Recommendation: Maintain current position with potential for 15-20% additional gains
    in the next quarter, subject to market conditions and economic indicators.
  `;

  const handleBalanceChange = (config: BalanceConfig) => {
    setCurrentBalance(config);
    console.log('Balance configuration updated:', config);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>
        TheNZT Financial Analysis - Preference-Aware Display
      </h1>

      {/* Preference status */}
      <div style={{
        backgroundColor: '#e3f2fd',
        padding: '1rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        border: '1px solid #bbdefb'
      }}>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#1976d2' }}>
          🧠 AI Preference Detection
        </h3>
        <p style={{ margin: '0.25rem 0', fontSize: '14px' }}>
          <strong>Detected Preference:</strong> {preferences.preference.toUpperCase()} 
          ({(preferences.confidence * 100).toFixed(0)}% confidence)
        </p>
        <p style={{ margin: '0.25rem 0', fontSize: '14px' }}>
          <strong>Reasoning:</strong> {preferences.reasoning}
        </p>
        <p style={{ margin: '0.25rem 0', fontSize: '14px' }}>
          <strong>Keywords Found:</strong> {preferences.keywords_found.join(', ')}
        </p>
      </div>

      {/* The main preference-aware component */}
      <PreferenceAwareBalance
        preferences={preferences}
        chartContent={<MockChart data={financialData} />}
        textContent={analysisText}
        onBalanceChange={handleBalanceChange}
        className="financial-analysis"
      />

      {/* Current configuration display */}
      {currentBalance && (
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: '1rem',
          borderRadius: '8px',
          marginTop: '2rem',
          border: '1px solid #ddd'
        }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#666' }}>
            ⚙️ Current Balance Configuration
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '14px' }}>
            <div><strong>Layout:</strong> {currentBalance.layout}</div>
            <div><strong>Emphasis:</strong> {currentBalance.emphasis}</div>
            <div><strong>Chart Size:</strong> {currentBalance.chartSize}</div>
            <div><strong>Text Size:</strong> {currentBalance.textSize}</div>
          </div>
        </div>
      )}

      {/* Integration notes */}
      <div style={{
        backgroundColor: '#fff3e0',
        padding: '1rem',
        borderRadius: '8px',
        marginTop: '2rem',
        border: '1px solid #ffcc02'
      }}>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#f57c00' }}>
          🔗 Integration Points
        </h3>
        <ul style={{ margin: '0.5rem 0', fontSize: '14px', paddingLeft: '1.5rem' }}>
          <li>Replace MockChart with actual TheNZT chart components</li>
          <li>Connect preference detection to TheNZT AI analysis pipeline</li>
          <li>Integrate with TheNZT response generation system</li>
          <li>Add persistence for user preference learning</li>
          <li>Connect to TheNZT styling and theme system</li>
        </ul>
      </div>

      {/* Manual preference override for testing */}
      <div style={{
        backgroundColor: '#f3e5f5',
        padding: '1rem',
        borderRadius: '8px',
        marginTop: '2rem',
        border: '1px solid #ce93d8'
      }}>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#7b1fa2' }}>
          🎮 Test Controls
        </h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {['visual', 'text', 'mixed'].map(pref => (
            <button
              key={pref}
              onClick={() => setPreferences({
                preference: pref as 'visual' | 'text' | 'mixed',
                confidence: 0.9,
                reasoning: `Manually set to ${pref} preference`,
                keywords_found: [pref]
              })}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: preferences.preference === pref ? '#7b1fa2' : '#fff',
                color: preferences.preference === pref ? '#fff' : '#7b1fa2',
                border: '1px solid #7b1fa2',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {pref.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FinancialAnalysisView;