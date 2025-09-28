'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { flushSync } from 'react-dom';
import { useSearchParams } from 'next/navigation';
import { useMessageStore } from '@/store/useZustandStore';
import { ArrowLeft, EllipsisVertical, ChevronLeft } from 'lucide-react';
import { TfiArrowUp } from 'react-icons/tfi';
import { axiosInstance } from '@/services/axiosInstance';
import ApiServices from '@/services/ApiServices';
import LoaderComponent from '@/components/Loader';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import useWindowDimension from '@/hooks/useWindowDimension';
import { toast } from 'sonner';

const FinanaceChart = dynamic(() => import('@/components/charts/FinanaceChart'), { ssr: false });

const Roles = { USER: 'user', ASSISTANT: 'assistant' };

interface ChatMessage {
  type: string;
  message: string;
}

export default function ChartInsights() {
  const data = useMessageStore((state) => state.financeChartModalData);
  const setData = useMessageStore((state) => state.setFinanceChartModalDataa);
  const searchParams = useSearchParams();
  const [questions, setQuestions] = useState([]);

  const messageId = searchParams.get('messageId') || '';
  const sessionId = searchParams.get('sessionId') || '';
  const exchange = searchParams.get('exchange') || '';
  const ticker = searchParams.get('ticker') || '';
  const router = useRouter();
  const chart_session_id = searchParams.get('chart_session_id') || '';

  const [selectedPeriod] = useState('1M');
  const [chatData, setChatData] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoadingResponse, setIsLoadingResponse] = useState(false);

  const [loading, setLoading] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const isFetchingRef = useRef(false);

  const { windowDimension } = useWindowDimension();
  const { width: windowWidth } = windowDimension;
  const [predictedChartData, setPredictedChartData] = useState([]);
  const isActive = predictedChartData.length > 0 && data.length > 0;

  const islg = windowWidth >= 1024;

  const getRelatedQueries = async () => {
    try {
      const payload = {
        ticker,
        exchange,
        name: data?.[0]?.realtime?.name || '',
        context_data: data,
        message_id: messageId,
        chart_session_id,
      };
      const response = await ApiServices.getStockPredictionData(
        data?.[0]?.realtime?.symbol || '',
        exchange,
        messageId,
        data?.[0]?.realtime?.name || ''
      );
      setPredictedChartData((response as any).combined_chart || []);
      const res = await ApiServices.fetchRelatedQueries(payload);
      setQuestions(res.related_queries);
    } catch (error) {
      toast('something went wrong, please try again');
    }
  };

  useEffect(() => {
    if (data.length > 0 && chart_session_id && messageId) {
      getRelatedQueries();
    }
  }, [data, chart_session_id, messageId]);

  useEffect(() => {
    if (!messageId && !chart_session_id) return;

    const formatChatHistory = (history: any[]): ChatMessage[] => {
      return history.flatMap((item) => [
        { type: Roles.USER, message: item.user_input },
        { type: Roles.ASSISTANT, message: item.response },
      ]);
    };

    if (chart_session_id) {
      const getSessionHistory = async () => {
        try {
          const res = await ApiServices.handleFetchStockSession(chart_session_id);

          if (Array.isArray(res)) {
            const formattedChat = formatChatHistory(res);
            setChatData(formattedChat);
          }
        } catch (error) {
          console.error('Error fetching related queries:', error);
        }
      };

      getSessionHistory();
    }
  }, [chart_session_id]);

  useEffect(() => {
    if (!messageId && !chart_session_id) return;
    if (data.length <= 0) {
      const fetchChartData = async () => {
        try {
          const response = await axiosInstance.post('/stock_data', {
            period: selectedPeriod,
            message_id: messageId,
            exchange_symbol: exchange,
            ticker,
          });

          if (response.data?.stock_data) {
            setData([response.data.stock_data]);
          }
        } catch (error) {
          console.error('Error fetching chart data:', error);
        }
      };

      fetchChartData();
    }
  }, [data, messageId, setData, chart_session_id]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [chatData, isLoadingResponse]);

  const handleQuestionClicked = useCallback(
    (question: string) => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;

      flushSync(() => {
        setChatData((prev) => [...prev, { type: Roles.USER, message: question }]);
      });

      setInput('');
      setIsLoadingResponse(true);

      const payload = {
        user_input: question,
        message_id: messageId,
        chart_session_id,
        session_id: sessionId,
        context_data: [{ ...data[0], predictive: predictedChartData }],
        ticker,
        exchange,
        name: data?.[0]?.realtime?.name || '',
      };

      requestIdleCallback(async () => {
        try {
          const response = await ApiServices.connectToChatBot(payload);
          setChatData((prev) => [...prev, { type: Roles.ASSISTANT, message: response.response }]);
        } catch (error) {
          console.error('Error fetching assistant response:', error);
          setChatData((prev) => [
            ...prev,
            { type: Roles.ASSISTANT, message: 'Something went wrong. Please try again.' },
          ]);
        } finally {
          isFetchingRef.current = false;
          setIsLoadingResponse(false);
        }
      });
    },
    [data, exchange, messageId, sessionId, ticker, predictedChartData]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = () => {
    if (!input.trim() || isLoadingResponse) return;
    handleQuestionClicked(input.trim());
  };

  const moveBackToQuery = () => {
    router.push(`/chat?search=${sessionId}`);
  };

  return (
    <>
      {Array.isArray(data) && data.length > 0 && predictedChartData.length > 0 ? (
        <div className="w-full lg:overflow-hidden lg:max-h-[100vh]" ref={!islg ? scrollRef : null}>
          {/* Header */}
          <div className="sticky top-0 z-10 bg-[#EEEBD7] px-4 py-3 flex items-center justify-between lg:py-8 lg:px-8 xl:px-20 lg:border-b">
            <button
              className="text-lg flex justify-center items-center gap-2"
              onClick={moveBackToQuery}
            >
              <ArrowLeft className="hidden lg:block" />
              <ChevronLeft className="lg:hidden" />
              <span className="text-black font-medium text-base font-schibstedGrotesk not-italic leading-none hidden lg:block">
                Back to query
              </span>
            </button>
            <h1 className="text-[#0A0A0A] font-schibstedGrotesk text-[20px] font-semibold lg:hidden">
              Chart insights
            </h1>
            <button className="text-lg">
              <EllipsisVertical />
            </button>
          </div>

          <div className="flex flex-col min-h-screen lg:min-h-0 bg-[#f8f6f3] text-[#111] lg:px-6 lg:bg-[#EEEBD7] ">
            <div className="bg-[#EEEBD7] rounded-t-[18px] lg:rounded-[0px] flex-1 flex flex-col lg:flex-row lg:px-10 pb-[70px]">
              {/* Chart */}
              <div className="w-full lg:w-2/3 px-2 sm:px-4 py-4 overflow-y-auto lg:overflow-hidden max-h-[calc(100vh-150px)] [&>*:first-child>*:first-child]:p-2 bg-[#EEEBD7]">
                <FinanaceChart
                  messageId={messageId}
                  chart_data={data}
                  isChartInsightRoute
                  financeChartModal
                  loading={loading}
                  setLoading={setLoading}
                />
              </div>

              {/* Chat + Input */}
              <div className="w-full lg:w-1/3 flex flex-col px-2 sm:px-4 py-4 space-y-4 relative lg:min-h-[80vh] lg:bg-[var(--primary-chart-bg)] lg:m-4 lg:mt-8 lg:rounded-[16px] lg:mb-[0]">
                {' '}
                <div className="hidden lg:block text-[#0A0A0A] font-schibstedGrotesk text-[20px] font-semibold not-italic leading-none ">
                  Chart Insights
                </div>
                <hr className="my-4 border-t border-gray-200 hidden lg:block" />
                <div
                  className="flex-1 flex flex-col justify-end overflow-y-auto lg:overflow-hidden lg:pr-4 lg:item-center"
                  style={{ maxHeight: 'calc(100vh)' }}
                >
                  <div className="space-y-2 lg:overflow-y-auto lg:max-h-[60vh] ">
                    {chatData.length > 0
                      ? chatData.map((msg, i) => (
                          <div
                            key={i}
                            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`p-4 text-base font-medium leading-6 text-[#191919] ${
                                msg.type === 'user'
                                  ? 'bg-[var(--primary-text-bg)] text-right rounded-bl-[12px] rounded-br-[12px] rounded-tl-[12px] rounded-tr-none'
                                  : ''
                              }`}
                            >
                              {msg.message}
                            </div>
                          </div>
                        ))
                      : null}

                    {isLoadingResponse && (
                      <div className="flex justify-start">
                        <div className="px-4 py-3 rounded-full text-sm bg-[#EEEBD7] animate-pulse">
                          Hang tight, your response is on the way...
                        </div>
                      </div>
                    )}
                    {islg && <div ref={scrollRef} />}
                  </div>

                  {/* Suggested Questions at Bottom When No Chat */}
                  {chatData.length === 0 && (
                    <div className="flex flex-col gap-2 pt-4">
                      {Array.isArray(questions) &&
                        questions.length > 0 &&
                        questions.map((q, i) => (
                          <div key={i} className="flex justify-start">
                            <button
                              className="text-[#0A0A0A] font-schibstedGrotesk text-[14px] font-medium leading-none gap-1 px-4 py-3 border border-[#E9E9E9] rounded-[38px] text-left"
                              onClick={() => handleQuestionClicked(q)}
                            >
                              {q}
                            </button>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
                {/* Sticky Input */}
                <div className="fixed bottom-0 left-0 w-full bg-[#EEEBD7] px-4 py-3 pt-5 lg:static lg:px-0 lg:bg-transparent">
                  <div className="relative w-full">
                    <input
                      type="text"
                      placeholder="Ask anything about this chart..."
                      className="p-3 w-full h-full rounded-lg bg-[#8181811A] text-black font-schibstedGrotesk placeholder:text-[#818181] text-sm pr-[50px] lg:bg-[#EEEBD7] lg:h-[52px]"
                      onChange={handleInputChange}
                      value={input}
                      name="user_input_chart"
                      id="user_input_chart"
                      onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                    />
                    <button
                      className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center border border-transparent size-[2.25rem] rounded-full disabled:bg-[rgba(113,161,141,0.10)] disabled:opacity-90 disabled:text-[#818181] text-white bg-[#4B9770]"
                      onClick={handleSubmit}
                      disabled={isLoadingResponse || !input.trim() || !isActive}
                    >
                      <TfiArrowUp size={20} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <LoaderComponent />
      )}
    </>
  );
}
