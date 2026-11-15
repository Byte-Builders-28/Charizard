import React, { useState, useRef, useEffect } from 'react'
import { askQuestion } from '../api/client.js'
import { Bot, Send, User, Sparkles, BookOpen, Quote, AlertCircle } from 'lucide-react'

const STARTER_QUESTIONS = [
  'Which experiments tested the lowest oxygen levels?',
  'What fuels were used in microgravity?',
  'Which investigations are most relevant to ISS fire safety?',
  'What is the partial-gravity gap?',
]

export default function AskAI() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hello, I am the FlameScope AI research assistant. Ask me anything about NASA microgravity combustion science experiments, fuel flammability, oxygen extinction limits, or spacecraft fire safety data.',
      citations: [],
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    document.title = 'FlameScope | Ask AI'
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async (qText) => {
    const textToSend = qText || input
    if (!textToSend.trim() || loading) return

    const userMessage = { role: 'user', text: textToSend }
    setMessages(prev => [...prev, userMessage])
    if (!qText) setInput('')
    setLoading(true)

    try {
      const response = await askQuestion(textToSend)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: response.answer || 'No response generated.',
          citations: response.citations || [],
        },
      ])
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: 'An error occurred while communicating with the analysis engine. Please try again.',
          citations: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Bot className="text-flame-500 w-8 h-8" />
          FlameScope Scientific QA
        </h1>
        <p className="text-gray-400 text-sm mt-1">
          Evidence-grounded conversational agent querying NASA PSI metadata, telemetry logs, and flight reports
        </p>
      </div>

      {/* Note Banner */}
      <div className="bg-space-800/80 border border-space-700 rounded-lg p-3 text-xs text-gray-300 flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-ember-400 flex-shrink-0" />
        <span>
          Grounded Responses: Every fact is mapped to source NASA PSI investigation records and experimental tables.
        </span>
      </div>

      {/* Messages Window */}
      <div className="flex-1 bg-space-800 rounded-xl border border-space-700 p-4 overflow-y-auto space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-flame-500/20 text-flame-400 flex items-center justify-center flex-shrink-0 border border-flame-500/30">
                <Bot className="w-5 h-5" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-xl p-4 text-sm ${
                m.role === 'user'
                  ? 'bg-flame-600 text-white'
                  : 'bg-space-900 text-gray-200 border border-space-700'
              }`}
            >
              <div className="leading-relaxed whitespace-pre-wrap">{m.text}</div>

              {/* Citations block */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-space-700">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 mb-2">
                    <BookOpen className="w-3.5 h-3.5 text-ember-400" />
                    <span>Evidence Citations ({m.citations.length}):</span>
                  </div>
                  <div className="space-y-2">
                    {m.citations.map((c, cIdx) => (
                      <div
                        key={cIdx}
                        className="bg-space-800/80 p-2.5 rounded-lg border border-space-700 text-xs"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-flame-400 uppercase tracking-wider bg-flame-500/10 px-1.5 py-0.5 rounded">
                            {c.investigation_id}
                          </span>
                          <span className="font-medium text-gray-300">{c.title}</span>
                          {c.source && (
                            <span className="text-[10px] text-gray-500 ml-auto bg-space-900 px-1.5 py-0.5 rounded">
                              {c.source}
                            </span>
                          )}
                        </div>
                        {c.quote && (
                          <div className="text-gray-400 italic flex items-start gap-1 pl-1">
                            <Quote className="w-3 h-3 text-gray-500 flex-shrink-0 mt-0.5" />
                            <span>"{c.quote}"</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-space-700 text-gray-300 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-flame-500/20 text-flame-400 flex items-center justify-center border border-flame-500/30">
              <Bot className="w-5 h-5" />
            </div>
            <div className="bg-space-900 text-gray-300 rounded-xl p-4 border border-space-700 text-sm flex items-center gap-3">
              <span className="animate-bounce">🔥</span>
              <span>Analyzing flight data and synthesizing scientific answer...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Starter Question Chips */}
      <div className="mt-3 flex flex-wrap gap-2">
        {STARTER_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="text-xs bg-space-800 hover:bg-space-700 text-gray-300 hover:text-white px-3 py-1.5 rounded-lg border border-space-700 transition-colors disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="mt-3 flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a technical combustion question (e.g. oxygen extinction limit in microgravity)..."
          disabled={loading}
          className="flex-1 bg-space-800 border border-space-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-flame-500 transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-flame-500 hover:bg-flame-600 disabled:opacity-50 text-white px-5 rounded-xl font-medium transition-colors flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  )
}

