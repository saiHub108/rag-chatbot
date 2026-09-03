import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState(
    'Who owns the partial refund issue and when should it be resolved?',
  )
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    if (question.trim().length < 3) {
      setError('Please enter at least three characters.')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'The request failed.')
      }

      setResult(data)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app">
      <header>
        <p>Local-first RAG application</p>
        <h1>AI Delivery Intelligence Copilot</h1>
        <p>
          Ask evidence-based questions about project risks, issues,
          dependencies and decisions.
        </p>
      </header>

      <form onSubmit={handleSubmit}>
        <label htmlFor="question">Ask about the project</label>

        <textarea
          id="question"
          rows="4"
          maxLength="500"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Analyzing project evidence...' : 'Ask Copilot'}
        </button>
      </form>

      {error && (
        <section role="alert">
          <h2>Unable to answer</h2>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section>
          <h2>Grounded answer</h2>
          <p>{result.answer}</p>

          <h2>Retrieved evidence</h2>

          {result.sources.map((source) => (
            <article key={source.source_number}>
              <h3>
                Source {source.source_number} — Similarity{' '}
                {source.similarity_score}
              </h3>
              <p>{source.content}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}

export default App