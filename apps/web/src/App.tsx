import { Routes, Route } from 'react-router-dom'

function HomePage() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <h2 className="mb-4 text-lg font-semibold">Chat Rooms</h2>
        <button className="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
          + New Chat
        </button>
      </aside>

      {/* Main Chat Area */}
      <main className="flex flex-1 flex-col">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <h1 className="text-xl font-semibold">Real Estate Assistant</h1>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mx-auto max-w-3xl">
            <p className="text-center text-gray-500">
              Start a conversation with your real estate assistant
            </p>
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="mx-auto flex max-w-3xl gap-2">
            <input
              type="text"
              placeholder="Ask about properties, market trends..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700"
            />
            <button className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700">
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  )
}

export default App
