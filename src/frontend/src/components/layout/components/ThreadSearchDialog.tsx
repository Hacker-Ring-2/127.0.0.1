'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Search } from 'lucide-react';
import { SessionHistoryData } from '../Sidebar';
import ApiServices from '@/services/ApiServices';
import { cn } from '@/lib/utils';
import { debounce } from '@/utils/utility';
import { useRouter } from 'next/navigation';
import LoaderComponent from '@/components/Loader';
import { handlePaginationData, PaginationResponse } from '@/utils/pagination';
import { useSessionHistoryStore } from '@/store/useSessionHistory';

interface ISearchThreadsDialog {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SearchThreadsDialog: React.FC<ISearchThreadsDialog> = ({ open, onOpenChange }) => {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [sessionTitlesData, setSessionTitlesData] = useState<SessionHistoryData>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const sessionHistoryData = useSessionHistoryStore((s) => s.sessionHistoryData);
  const hasMoreRef = useRef(true);
  const pageRef = useRef(1);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const abortController = useRef<AbortController | null>(null);
  const lastFetchRef = useRef<{ input: string; page: number } | null>(null);

  const getThreadTitle = useCallback(async (input: string, page: number): Promise<void> => {
    if (
      historyLoading ||
      (!hasMoreRef.current && page !== 1) ||
      (lastFetchRef.current?.input === input && lastFetchRef.current?.page === page)
    ) {
      return;
    }

    lastFetchRef.current = { input, page };
    setHistoryLoading(true);

    try {
      abortController.current?.abort();
      abortController.current = new AbortController();

      const response = await ApiServices.getSessionTitle(
        input,
        abortController.current.signal,
        page,
        10
      );

      if (response.data && response.data.data) {
        const paginationResponse: PaginationResponse = {
          data: {
            data: response.data.data as SessionHistoryData
          }
        };
        setSessionTitlesData((prev) => handlePaginationData(paginationResponse, prev));
        hasMoreRef.current = response.data.has_more || false;
      }
      pageRef.current += 1;
    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was cancelled');
      }
    } finally {
      setHistoryLoading(false);
    }
  }, [historyLoading]);

  const debouncedGetThreadTitleRef = useRef(
    debounce((value = '', page: number) => {
      getThreadTitle(value, page);
    }, 300)
  );

  useEffect(() => {
    if (open && sessionHistoryData) {
      pageRef.current = 1;
      setSessionTitlesData(sessionHistoryData);
    }
    const debouncedFunction = debouncedGetThreadTitleRef.current;
    return () => {
      debouncedFunction?.cancel?.();
    };
  }, [open, sessionHistoryData]);

  useEffect(() => {
    let observer: IntersectionObserver;

    requestAnimationFrame(() => {
      if (!scrollRef.current || !bottomRef.current) return;

      observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting && !historyLoading && hasMoreRef.current) {
            getThreadTitle(searchQuery, pageRef.current);
          }
        },
        {
          root: scrollRef.current,
          threshold: 0.1,
        }
      );

      observer.observe(bottomRef.current);
    });

    return () => observer?.disconnect();
  }, [searchQuery, historyLoading, getThreadTitle]);

  const handleClose = (open: boolean) => {
    abortController.current?.abort();
    debouncedGetThreadTitleRef.current.cancel();
    setSearchQuery('');
    setSessionTitlesData([]);
    hasMoreRef.current = true;
    pageRef.current = 1;
    onOpenChange(open);
  };

  const handleSearchThread = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.trim();
    setSearchQuery(value);
    pageRef.current = 1;
    setSessionTitlesData([]);
    hasMoreRef.current = true;

    // Cancel in-flight request and debounce
    abortController.current?.abort();
    debouncedGetThreadTitleRef.current.cancel();
    debouncedGetThreadTitleRef.current(value, pageRef.current);
  };

  const handleSessionTiltleClick = (sessionId: string): void => {
    router.push(`/chat?search=${sessionId}`);
    setTimeout(() => handleClose(false), 300);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="w-full max-w-xl mx-auto bg-primary-light rounded-lg p-0 gap-0 ">
        <DialogHeader className="px-4 pt-6 pb-0">
          <DialogTitle className="p-0">
            <div className="relative mt-6 mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" />
              <input
                onChange={handleSearchThread}
                type="text"
                placeholder="Search Threads"
                className={`block w-full pl-10 pr-3 py-3 bg-[var(--primary-chart-bg)] rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200`}
              />
            </div>
          </DialogTitle>
        </DialogHeader>

        <div
          className="px-4 flex-1 h-[260px] max-h-[50dvh] overflow-y-auto bg-[var(--primary-main-bg)]"
          ref={scrollRef}
        >
          <div>
            {sessionTitlesData.map((group, gi) => (
              <div key={gi}>
                <div className="pb-1.5 text-sm font-medium text-black">{group.timeline}</div>
                {group.data.map((item) => (
                  <div
                    onClick={() => handleSessionTiltleClick(item.id)}
                    key={item.id}
                    className={cn(
                      'px-2 py-3 flex items-center cursor-pointer rounded-md font-semibold text-sm transition-colors text-neutral-300 hover:bg-[var(--primary-chart-bg)] hover:text-[#181818]'
                    )}
                  >
                    <span className="flex-1 min-w-0 truncate">{item.title}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>

          {!hasMoreRef.current && (
            <div className="text-center py-8">
              {sessionTitlesData.length > 0
                ? 'You’ve reached the end of the list.'
                : `No threads found for “${searchQuery}”`}
            </div>
          )}
          {historyLoading && <LoaderComponent height={40} />}
          {!historyLoading && hasMoreRef.current && <div ref={bottomRef} className="h-10" />}
        </div>
      </DialogContent>
    </Dialog>
  );
};
