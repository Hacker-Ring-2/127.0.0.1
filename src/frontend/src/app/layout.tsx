// app/layout.tsx
'use client';

import { Schibsted_Grotesk } from 'next/font/google';
import './globals.css';
import './styles.css';
import { Toaster } from 'sonner';
import { useEffect, useState, useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { verifyToken } from '@/utils/auth';
import { useAuthStore } from '@/store/useZustandStore';
import LoaderComponent from '@/components/Loader';
import NextTopLoader from 'nextjs-toploader';
import Head from 'next/head';

const fustat = Schibsted_Grotesk({
  variable: '--font-fustat',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [isLoading, setIsLoading] = useState(true);
  const pathname = usePathname();
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const noSidebarPages = useMemo(() => ['/login', '/signup', '/reset-password', '/onbording'], []);

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);

      // Skip verification if on public pages (login, signup, etc.)
      if (noSidebarPages.includes(pathname)) {
        setIsLoading(false);
        return;
      }

      // Skip verification if already authenticated in store
      if (isAuthenticated) {
        setIsLoading(false);
        return;
      }

      // Otherwise verify the token
      const isValid = await verifyToken();

      if (isValid) {
        if (noSidebarPages.includes(pathname)) {
          router.push('/');
        }
      } else {
        if (!noSidebarPages.includes(pathname)) {
          router.push('/login');
        }
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [pathname, router, isAuthenticated, noSidebarPages]);

  return (
    <html lang="en" className={`${fustat.variable}`}>
      <Head>
        <link rel="apple-touch-icon" sizes="57x57" href="/apple-icon-57x57.png" />
        <link rel="apple-touch-icon" sizes="114x114" href="/apple-icon-114x114.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <title>hiiiiiiiiiiiiiiiii</title>
      </Head>
      <body>
        {/* NextTopLoader should always be rendered */}
        <NextTopLoader
          color="#954767"
          initialPosition={0.08}
          crawlSpeed={200}
          height={3}
          crawl={true}
          showSpinner={false}
          easing="ease"
          speed={200}
          shadow="0 0 10px #954767,0 0 5px #954767"
        />

        {isLoading ? (
          <LoaderComponent />
        ) : (
          <>
            {children}
            <Toaster richColors position="top-center" />
          </>
        )}
      </body>
    </html>
  );
}
