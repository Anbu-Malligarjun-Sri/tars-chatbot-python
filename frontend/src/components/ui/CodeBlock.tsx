import { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CodeBlockProps {
  code: string;
  language?: string;
}

export function CodeBlock({ code, language = 'plaintext' }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Safer syntax highlighting that avoids HTML injection loops
  const highlightCode = (codeStr: string) => {
    // 1. Escape HTML first to prevent XSS and confusing the parser
    const escaped = codeStr
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // 2. Define token patterns
    const patterns = [
      { type: 'comment', regex: /(#.*$|\/\/.*$|\/\*[\s\S]*?\*\/)/gm, color: 'text-muted-foreground/60' },
      { type: 'string', regex: /(["'`])(?:(?!\1|\\).|\\.)*\1/g, color: 'text-tars-green' },
      { type: 'keyword', regex: /\b(def|class|function|const|let|var|return|if|else|for|while|import|from|export|async|await|try|catch|finally|throw|new|this|self|True|False|None|null|undefined|true|false|int|float|string|void|public|private|protected|static|namespace|using|include|package)\b/g, color: 'text-tars-blue font-semibold' },
      { type: 'number', regex: /\b(\d+\.?\d*)\b/g, color: 'text-tars-amber' },
      { type: 'function', regex: /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g, color: 'text-tars-purple' },
    ];

    // Simple tokenizer:
    // We can't easily do a full tokenizer in one pass without a parser library.
    // For now, to solve the "HTML tag corruption" issue, we will just disable the 
    // problematic sequential highlighting that breaks when keywords appear in strings.
    // A full tokenizer is too complex for this single file without adding dependencies.
    //
    // ALTERNATIVE: Use a lighter approach - only highlight if we are sure we are not inside a tag.
    // But since we are creating HTML tags, it's recursive.
    
    // Let's stick to a simpler, safe list of replacements that DON'T overlap significantly
    // OR just use a placeholder strategy.
    
    // Placeholder strategy:
    // 1. Extract strings and comments -> replace with placeholders
    // 2. Highlight keywords/numbers in the remaining text
    // 3. Restore placeholders (wrapped in spans)
    
    const tokens: {id: string, content: string, color: string}[] = [];
    let processed = escaped;
    
    // Helper to store token and get placeholder
    const storeToken = (match: string, color: string) => {
      const id = `__TOKEN_${tokens.length}__`;
      tokens.push({ id, content: match, color });
      return id;
    };

    // 1. Extract Strings & Comments (highest priority, can contain other keywords)
    processed = processed.replace(patterns[0].regex, (match) => storeToken(match, patterns[0].color)); // Comments
    processed = processed.replace(patterns[1].regex, (match) => storeToken(match, patterns[1].color)); // Strings

    // 2. Highlight Keywords & Others in the remaining "safe" text
    processed = processed.replace(patterns[2].regex, (match) => `<span class="${patterns[2].color}">${match}</span>`); // Keywords
    processed = processed.replace(patterns[3].regex, (match) => `<span class="${patterns[3].color}">${match}</span>`); // Numbers
    processed = processed.replace(patterns[4].regex, (match, p1) => `<span class="${patterns[4].color}">${p1}</span>(`); // Functions

    // 3. Restore tokens
    tokens.forEach(token => {
      processed = processed.replace(token.id, `<span class="${token.color}">${token.content}</span>`);
    });

    return processed;
  };

  return (
    <div className="relative group my-3 rounded overflow-hidden border border-border/50 bg-tars-black/50">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-tars-dark/80 border-b border-border/30">
        <span className="font-terminal text-[10px] uppercase tracking-wider text-muted-foreground">
          {language}
        </span>
        <motion.button
          onClick={handleCopy}
          whileTap={{ scale: 0.95 }}
          className={cn(
            "flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-terminal uppercase tracking-wider transition-all",
            copied 
              ? "bg-tars-green/20 text-tars-green" 
              : "bg-tars-silver/50 text-muted-foreground hover:text-tars-light hover:bg-tars-silver"
          )}
        >
          {copied ? (
            <>
              <Check className="w-3 h-3" />
              COPIED
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              COPY
            </>
          )}
        </motion.button>
      </div>
      
      {/* Code Content */}
      <pre className="p-4 overflow-x-auto scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        <code 
          className="font-mono text-sm text-tars-light leading-relaxed"
          dangerouslySetInnerHTML={{ __html: highlightCode(code) }}
        />
      </pre>
    </div>
  );
}
