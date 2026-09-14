import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, Send, Bot, User, Sparkles } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { API_BASE_URL } from '../api';

export default function AIChat() {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState([
    { role: 'assistant', content: t('chat.welcome') }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  // Use a ref to accumulate streamed text — immune to StrictMode double-calls
  const streamedTextRef = useRef('');

  // Update welcome message if language changes and it's the only message
  useEffect(() => {
    if (messages.length === 1 && messages[0].role === 'assistant') {
      setMessages([{ role: 'assistant', content: t('chat.welcome') }]);
    }
  }, [language]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = { role: 'user', content: input };
    const currentMessages = [...messages, userMessage];
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    streamedTextRef.current = '';

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          messages: currentMessages.map(m => ({ role: m.role, content: m.content })),
          language: language
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error('ReadableStream not supported.');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      // Add the empty assistant message first
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      let buffer = '';
      let streamDone = false;

      while (!streamDone) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.content) {
                // Accumulate into a ref (not subject to StrictMode double-calls)
                streamedTextRef.current += data.content;
                const currentText = streamedTextRef.current;
                // Set state with the full accumulated text, not appending
                setMessages(prev => {
                  const updated = prev.slice(0, -1);
                  return [...updated, { role: 'assistant', content: currentText }];
                });
              }
              if (data.done) {
                streamDone = true;
              }
            } catch (parseErr) {
              // skip malformed SSE lines
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: t('chat.error') }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleStarter = (question) => {
    setInput(question);
    setTimeout(() => {
      document.getElementById('send-button')?.click();
    }, 100);
  };

  const starters = language === 'my' ? [
    "မြန်မာနိုင်ငံ အပူပိုင်းဇုန်မှာ ဘယ်သီးနှံတွေ အဖြစ်ထွန်းဆုံးလဲ?",
    "မိုးရေချိန်က စပါးအထွက်နှုန်းအပေါ် ဘယ်လိုသက်ရောက်မှုရှိလဲ?",
    "NDVI ဆိုတာဘာလဲ၊ အပင်ကျန်းမာရေးကို ဘယ်လိုတိုင်းတာလဲ?",
    "အက်စစ်ဓာတ်များတဲ့ မြေနဲ့ မိုးများတဲ့နေရာအတွက် သီးနှံအကြံပြုပေးပါ"
  ] : [
    "What crops grow best in Myanmar's dry zone?",
    "How does rainfall affect rice yields?",
    "What is NDVI and how does it measure vegetation health?",
    "Recommend crops for acidic soil with high rainfall"
  ];

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2 className="m-0 text-xl font-semibold"><MessageCircle size={28} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '10px' }}/> {t('chat.title')}</h2>
        <div className="llm-badge">
          <Sparkles size={14} /> {t('chat.powered')}
        </div>
      </div>
      
      <div className="glass-panel chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className={`message-avatar ${msg.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
              {msg.role === 'user' ? <User size={20} color="white" /> : <Bot size={20} color="white" />}
            </div>
            <div className={`message-bubble ${msg.role === 'user' ? 'user-bubble' : 'bot-bubble'} ${isTyping && idx === messages.length - 1 && msg.role === 'assistant' ? 'streaming-cursor' : ''}`}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {isTyping && messages[messages.length - 1]?.role === 'user' && (
          <div className="chat-message assistant">
            <div className="message-avatar bot-avatar">
              <Bot size={20} color="white" />
            </div>
            <div className="message-bubble bot-bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="starter-chips">
          {starters.map((q, i) => (
            <button key={i} className="starter-chip" onClick={() => handleStarter(q)}>{q}</button>
          ))}
        </div>
      )}

      <form className="chat-input-container" onSubmit={handleSend}>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('chat.placeholder')}
          disabled={isTyping}
        />
        <button id="send-button" type="submit" className="btn btn-primary" disabled={!input.trim() || isTyping}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}
