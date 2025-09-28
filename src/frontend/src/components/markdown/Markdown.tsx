import { cn } from '@/lib/utils';
import { omit } from 'lodash';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { PluggableList } from 'unified';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkDirective from 'remark-directive';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { visit } from 'unist-util-visit';
import { Download } from 'lucide-react';

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || '';

import { AspectRatio } from '@/components/ui/aspect-ratio';
import { Separator } from '@/components/ui/separator';
import {
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import CodeSnippet from './CodeSnippet';
import BlinkingCursor from './BlinkingCursor';
import { alertComponents } from './MarkdownAlert';
import CustomTable from './CustomTable';
import { toast } from 'sonner';
import EnhancedGraphRenderer from './EnhancedGraphRenderer';

interface Props {
  allowHtml?: boolean;
  latex?: boolean;
  children: string;
  isProcessing: boolean;
  className?: string;
}

interface PreComponentProps extends React.HTMLAttributes<HTMLPreElement> {
  children?: React.ReactNode;
  isProcessing: boolean;
}

interface TreeNode {
  type: string;
  value?: string;
  children?: TreeNode[];
}

interface VisitNode {
  type: string;
  value?: string;
  data?: { [key: string]: unknown };
}

interface ReactElementWithProps {
  props?: { 
    className?: string; 
    children?: React.ReactNode;
  };
}

interface ImageProps {
  src?: string;
  alt?: string;
  title?: string;
}

interface IframeProps {
  src?: string;
  title?: string;
}

// Separate component for pre element to handle React Hooks properly
const PreComponent: React.FC<PreComponentProps> = ({ children, isProcessing, ...props }) => {
  const [content, setContent] = useState('');
  const [isReady, setIsReady] = useState(false);

  const getContent = useCallback((node: React.ReactNode): string => {
    if (typeof node === 'string') return node;
    if (node && typeof node === 'object' && 'props' in node) {
      const nodeWithProps = node as ReactElementWithProps;
      if (nodeWithProps.props?.children) return getContent(nodeWithProps.props.children);
    }
    return '';
  }, []);

  // detect code‑blocks marked "language-graph" OR plain text containing graph JSON
  const isGraphBlock = useMemo(() => {
    console.log('🔍 Checking isGraphBlock for:', children);
    
    // Check for language-graph code blocks (after preprocessing)
    if (children &&
        typeof children === 'object' &&
        (children as ReactElementWithProps).props?.className?.includes('language-graph')) {
      console.log('✅ Found language-graph code block');
      return true;
    }
    
    // Check for plain text containing graph JSON patterns (fallback)
    const textContent = getContent(children);
    console.log('📝 Text content preview:', textContent?.substring(0, 200) + '...');
    
    if (textContent) {
      // Check for various graph patterns
      if (textContent.includes('<END_OF_GRAPH>') && 
          (textContent.includes('{"chart_collection":') || 
           textContent.includes('graph {') || 
           textContent.includes('graph\n{'))) {
        console.log('✅ Found plain text graph pattern');
        return true;
      }
    }
    
    console.log('❌ No graph pattern detected');
    return false;
  }, [children, getContent]);

  useEffect(() => {
    if (!isGraphBlock) return;

    const raw = getContent(children);
    console.log((children as ReactElementWithProps)?.props?.children, 'children');
    
    // Add null/undefined safety checks
    if (!raw || typeof raw !== 'string') {
      setIsReady(false);
      return;
    }
    
    // Handle multiple graph formats
    let jsonText = '';
    
    if (raw.includes('<END_OF_GRAPH>') && !isProcessing) {
      if (raw.includes('graph\n')) {
        // Format: "graph\n{...}<END_OF_GRAPH>"
        const match = raw.match(/graph\n([\s\S]*?)<END_OF_GRAPH>/);
        if (match && match[1]) {
          jsonText = match[1].trim();
        }
      } else if (raw.includes('graph {')) {
        // Format: "graph {...}<END_OF_GRAPH>" (same line)
        const match = raw.match(/graph\s*(\{[\s\S]*?)<END_OF_GRAPH>/);
        if (match && match[1]) {
          jsonText = match[1].trim();
        }
      } else if (raw.startsWith('{') && raw.includes('"chart_collection"')) {
        // Format: "{...}<END_OF_GRAPH>" (direct JSON)
        jsonText = raw.replace('<END_OF_GRAPH>', '').trim();
      }
      
      if (jsonText) {
        console.log('Extracted JSON for graph rendering:', jsonText);
        setContent(jsonText);
        setIsReady(true);
      } else {
        console.log('No valid JSON found in graph content:', raw);
        setIsReady(false);
      }
    } else {
      // still streaming…
      setIsReady(false);
    }
  }, [children, isGraphBlock, isProcessing, getContent]);

  if (!isGraphBlock) {
    return <CodeSnippet {...props}>{children}</CodeSnippet>;
  }

  if (!isReady) {
    return (
      <div className="bg-gray-100 border border-gray-300 rounded-md p-4 my-4">
        <div className="flex items-center space-x-2 mb-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
          <span className="text-sm text-gray-600">Loading graph…</span>
        </div>
        <pre className="text-xs text-gray-500 overflow-hidden max-h-20">
          <code>{content}</code>
        </pre>
      </div>
    );
  }

  // when valid JSON is in `content`, render
  try {
    return <EnhancedGraphRenderer codeContent={content} />;
  } catch {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 my-4">
        <div className="text-red-600 text-sm mb-2">Error rendering graph</div>
        <pre className="text-xs text-gray-500 max-h-20 overflow-auto">
          <code>{content}</code>
        </pre>
      </div>
    );
  }
};

const cursorPlugin = () => {
  return (tree: TreeNode) => {
    visit(tree, 'text', (node: VisitNode, index, parent) => {
      const placeholderPattern = /\u200B/g;
      const matches = [...(node.value?.matchAll(placeholderPattern) || [])];

      if (matches.length > 0) {
        const newNodes: VisitNode[] = [];
        let lastIndex = 0;

        matches.forEach((match) => {
          const matchIndex = match.index || 0;

          // Add text before cursor
          if (matchIndex > lastIndex) {
            newNodes.push({
              type: 'text',
              value: node.value?.substring(lastIndex, matchIndex) || '',
            });
          }

          // Add cursor component
          newNodes.push({
            type: 'blinkingCursor',
            data: { hName: 'blinkingCursor' },
          });

          lastIndex = matchIndex + match[0].length;
        });

        // Add remaining text
        if (lastIndex < (node.value?.length || 0)) {
          newNodes.push({
            type: 'text',
            value: node.value?.substring(lastIndex) || '',
          });
        }

        // Replace current node with new nodes
        if (parent && typeof index === 'number') {
          (parent as TreeNode).children?.splice(index, 1, ...newNodes);
        }
      }
    });
  };
};

const Markdown: React.FC<Props> = ({
  allowHtml = false,
  latex = false,
  children,
  isProcessing,
  className,
}) => {
  const cleanedContent = useMemo(() => {
    // Remove empty lines at the beginning
    const lines = children.split('\n');
    const firstNonEmptyIndex = lines.findIndex((line) => line.trim() !== '');
    return firstNonEmptyIndex > 0
      ? lines.slice(firstNonEmptyIndex).join('\n')
      : children;
  }, [children]);

  const processedChildren = useMemo(() => {
    const baseContent = typeof cleanedContent === 'string' ? cleanedContent : children;
    if (typeof baseContent !== 'string') return baseContent;
    
    console.log('🔍 Processing content length:', baseContent.length);
    
    // Test regex patterns
    const graphPattern = /graph\s*(\{"chart_collection":.+?<END_OF_GRAPH>)/g;
    const matches = [...baseContent.matchAll(graphPattern)];
    
    console.log('📊 Found graph matches:', matches.length);
    if (matches.length > 0) {
      console.log('📊 First match preview:', matches[0][0].substring(0, 100) + '...');
    }
    
    // Convert plain text graph patterns to proper markdown code blocks
    const processed = baseContent.replace(
      graphPattern,
      '\n\n```graph\n$1\n```\n\n'
    );
    
    // Debug logging
    if (processed !== baseContent) {
      console.log('📊 Graph preprocessing applied!');
      console.log('Original length:', baseContent.length);
      console.log('Processed length:', processed.length);
      console.log('Conversion preview:', processed.substring(processed.indexOf('```graph'), processed.indexOf('```graph') + 200) + '...');
    } else {
      console.log('❌ No graph conversion applied');
      // Check if content contains graph-like patterns
      if (baseContent.includes('chart_collection')) {
        console.log('⚠️ Content has chart_collection but no match');
        console.log('Content sample:', baseContent.substring(baseContent.indexOf('chart_collection') - 50, baseContent.indexOf('chart_collection') + 100));
      }
    }
    
    return processed;
  }, [children, cleanedContent]);

  const plugins = useMemo(() => {
    let rehypePlugins: PluggableList = [];
    let remarkPlugins: PluggableList = [];

    if (allowHtml) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      rehypePlugins = [rehypeRaw as any, ...rehypePlugins];
    }
    if (latex) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      rehypePlugins = [[rehypeKatex as any, { strict: false }], ...rehypePlugins];
    }

    remarkPlugins = [
      ...remarkPlugins,
      // MarkdownAlert, // Temporarily disabled to test
      cursorPlugin,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      remarkGfm as any,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      remarkDirective as any,
    ];

    if (latex) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      remarkPlugins = [...remarkPlugins, remarkMath as any];
    }

    return { rehypePlugins, remarkPlugins };
  }, [allowHtml, latex]);

  return (
    <div className={cn('markdown prose prose-neutral max-w-none', className)}>
      <ReactMarkdown
        rehypePlugins={plugins.rehypePlugins}
        remarkPlugins={plugins.remarkPlugins}
        components={{
          code(props) {
            console.log('props', props);
            return (
              <code
                {...omit(props, ['node'])}
                className="relative rounded px-[0.3rem] py-[0.2rem] text-sm font-semibold bg-[#CDDCC4] text-[#181818] italic "
              />
            );
          },

          // Graph-aware pre component using proper React component
          pre: (props: React.HTMLAttributes<HTMLPreElement> & { children?: React.ReactNode }) => (
            <PreComponent {...props} isProcessing={isProcessing} />
          ),

          // Graph-aware paragraph component to catch graph content in regular paragraphs
          p: (props: React.HTMLAttributes<HTMLParagraphElement> & { children?: React.ReactNode }) => {
            // Extract text content from children recursively
            const extractText = (node: React.ReactNode): string => {
              if (typeof node === 'string') return node;
              if (node && typeof node === 'object' && 'props' in node) {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                return extractText((node as any).props?.children);
              }
              return '';
            };
            
            const textContent = extractText(props.children);
            
            if (textContent && 
                textContent.includes('<END_OF_GRAPH>') && 
                (textContent.includes('graph {') || textContent.includes('{"chart_collection":'))) {
              // This paragraph contains graph content, create compatible props for PreComponent
              console.log('Found graph content in paragraph:', textContent);
              const preProps: React.HTMLAttributes<HTMLPreElement> & { children?: React.ReactNode } = {
                children: props.children,
                className: props.className,
              };
              return <PreComponent {...preProps} isProcessing={isProcessing} />;
            }
            
            // Regular paragraph
            return <p {...omit(props, ['node'])} className="text-[#0A0A0A] my-4" />;
          },

          a({ children, ...props }) {
            return (
              <a
                {...props}
                className="w-fit inline-block group"
                target="_blank"
                rel="noopener noreferrer"
                title={props.href}
              >
                <div className="border border-[#DDDAC9] text-[#A7A7A7] hover:text-gray-500 rounded-[60px] text-[10px] px-2 py-0.5 opacity-90 hover:opacity-100 flex items-center w-fit transition-all duration-200">
                  <span className="text-xs font-medium text-[#000000]">{children}</span>
                </div>
              </a>
            );
          },
          iframe: ({ src, title, ...props }: IframeProps & React.HTMLAttributes<HTMLIFrameElement>) => {
            return (
              <div className="my-4 w-full relative overflow-hidden">
                <AspectRatio
                  ratio={16 / 9}
                  className="overflow-hidden rounded-md h-auto sm:min-height-0 min-height-[50dvh]"
                >
                  <iframe
                    src={src?.startsWith('public') ? `${BASE_URL}/${src}` : src}
                    title={title || 'Embedded content'}
                    width="100%"
                    height="100%"
                    allowFullScreen
                    className="h-full w-full border-none responsive-zoom"
                    {...props}
                  />
                </AspectRatio>
              </div>
            );
          },
          img: (image: ImageProps) => {
            if (!image.src) return null;
            
            const isFromPublic = image.src.startsWith('public');
            const imageSrc = isFromPublic ? `${BASE_URL}/${image.src}` : image.src;

            const handleDownload = async () => {
              try {
                const response = await fetch(imageSrc);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = (image.src || '').split('/').pop() || 'image';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                toast.success('Image downloaded successfully');
              } catch (error) {
                toast.error('Failed to download image');
                console.error('Download failed:', error);
              }
            };

            return (
              <div className="group relative w-full">
                <div className="relative overflow-hidden rounded-lg border border-gray-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={imageSrc}
                    alt={image.alt}
                    className="h-auto w-full object-contain"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 transition-all duration-200 group-hover:bg-opacity-10">
                    <button
                      onClick={handleDownload}
                      className="flex items-center space-x-2 rounded-full bg-white px-3 py-1.5 text-sm font-medium text-gray-700 opacity-0 shadow-lg transition-all duration-200 hover:bg-gray-50 group-hover:opacity-100"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>
                {image.title && (
                  <p className="mt-2 text-center text-sm text-gray-600">{image.title}</p>
                )}
              </div>
            );
          },
          h1(props) {
            return (
              <h1
                {...omit(props, ['node'])}
                className="scroll-m-20 text-4xl font-bold tracking-tight lg:text-5xl mt-8 first:mt-0"
              />
            );
          },
          h2(props) {
            return (
              <h2
                {...omit(props, ['node'])}
                className="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight first:mt-0 mt-8"
              />
            );
          },
          h3(props) {
            return (
              <h3
                {...omit(props, ['node'])}
                className="scroll-m-20 text-2xl font-semibold tracking-tight mt-6 first:mt-0"
              />
            );
          },
          ul: (props) => (
            <ul {...omit(props, ['node'])} className="my-6 ml-6 list-disc [&>li]:mt-2" />
          ),
          ol: (props) => (
            <ol {...omit(props, ['node'])} className="my-6 ml-6 list-decimal [&>li]:mt-2" />
          ),
          li: (props) => <li {...omit(props, ['node'])} className="text-[#0A0A0A]" />,
          blockquote: (props) => (
            <blockquote
              {...omit(props, ['node'])}
              className="mt-6 border-l-2 pl-6 italic border-[#D2D2D2] text-[#6F6F6F]"
            />
          ),
          hr: () => <Separator className="my-4 md:my-8" />,
          strong: (props) => (
            <strong {...omit(props, ['node'])} className="font-semibold text-[#0A0A0A]" />
          ),
          h4(props) {
            return (
              <h4
                {...omit(props, ['node'])}
                className="scroll-m-20 text-xl font-semibold tracking-tight mt-6 first:mt-0"
              />
            );
          },
          h5(props) {
            return (
              <h5
                {...omit(props, ['node'])}
                className="scroll-m-20 text-lg font-semibold tracking-tight mt-6 first:mt-0"
              />
            );
          },
          h6(props) {
            return (
              <h6
                {...omit(props, ['node'])}
                className="scroll-m-20 text-base font-semibold tracking-tight mt-6 first:mt-0"
              />
            );
          },
          table: ({ children }) => {
            return <CustomTable>{children}</CustomTable>;
          },
          thead({ children }) {
            return (
              <TableHeader className="bg-[#F3F1EE]">
                {children}
              </TableHeader>
            );
          },
          tr({ children }) {
            return (
              <TableRow className="">
                {children}
              </TableRow>
            );
          },
          th({ children }) {
            return (
              <TableHead
                className="border-l border-r px-2.5 border-[#D2D2D2] first:border-l-0 last:border-r-0"
              >
                {children}
              </TableHead>
            );
          },
          td({ children }) {
            return (
              <TableCell
                className="border-l border-r px-2.5 border-[#E8E3D1] first:border-l-0 last:border-r-0"
              >
                {children}
              </TableCell>
            );
          },
          tbody({ children }) {
            return <TableBody>{children}</TableBody>;
          },
          // @ts-expect-error custom plugin
          blinkingCursor: () => <BlinkingCursor whitespace />,
          // Alert components for ::: syntax
          ...alertComponents,
        }}
      >
        {processedChildren}
      </ReactMarkdown>
    </div>
  );
};

export default React.memo(Markdown);