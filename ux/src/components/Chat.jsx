import { useState, useRef, useEffect } from 'react'
import './Chat.css'

function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const [isExpanded, setIsExpanded] = useState(true)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      // Call backend API with streaming
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          thread_id: 'session-1'
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      // Create assistant message
      let assistantMessage = ''
      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.token) {
                assistantMessage += data.token
                // Update the last message
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    role: 'assistant',
                    content: assistantMessage
                  }
                  return newMessages
                })
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Error connecting to chat server. Make sure the backend is running on port 8000.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`chat-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="chat-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="chat-title">
          <span className="chat-icon">💬</span>
          <span>AI Assistant</span>
        </div>
        <button className="chat-toggle">
          {isExpanded ? '→' : '←'}
        </button>
      </div>

      {isExpanded && (
        <>
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <div className="welcome-icon">👋</div>
                <p>Hi! I can help you with questions about:</p>
                <ul>
                  <li>Window, door, and appliance specifications</li>
                  <li>Cost analysis and alternatives</li>
                  <li>Unit types and floor distributions</li>
                  <li>RSMeans pricing data</li>
                </ul>
                <p className="welcome-prompt">Ask me anything!</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  {msg.content}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about costs, materials, alternatives..."
              disabled={isLoading}
              className="chat-input"
            />
            <button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="chat-send-button"
            >
              ➤
            </button>
          </form>
        </>
      )}
    </div>
  )
}

export default Chat


