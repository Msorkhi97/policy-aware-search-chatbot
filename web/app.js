const chatLog = document.getElementById("chat-log")
const form = document.getElementById("chat-form")
const input = document.getElementById("chat-input")
const sourcesList = document.getElementById("sources-list")

let history = []

function addBubble(role, text) {
  const bubble = document.createElement("div")
  bubble.className = `bubble ${role}`
  bubble.textContent = text
  chatLog.appendChild(bubble)
  chatLog.scrollTop = chatLog.scrollHeight
}

function renderSources(sources) {
  sourcesList.innerHTML = ""

  if (!sources || sources.length === 0) {
    sourcesList.textContent = "منبعی برای این پاسخ استفاده نشد."
    return
  }

  for (const source of sources) {
    const item = document.createElement("div")
    item.className = "source-item"

    const link = document.createElement("a")
    link.href = source.url || "#"
    link.target = "_blank"
    link.textContent = source.title

    const snippet = document.createElement("p")
    snippet.textContent = source.content.slice(0, 120) + "..."

    item.appendChild(link)
    item.appendChild(snippet)
    sourcesList.appendChild(item)
  }
}

addBubble(
  "assistant",
  "سلام! من یک چت‌بات جست‌وجومحورم، جواب‌هام رو فقط از منابع بیرونی (مثل ویکی‌پدیا) می‌گیرم و به سوال‌های سیاسی پاسخ نمی‌دم. بپرس!",
)

form.addEventListener("submit", async (event) => {
  event.preventDefault()

  const question = input.value.trim()
  if (!question) return

  input.value = ""
  input.disabled = true
  addBubble("user", question)

  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  })

  addBubble("assistant", "")
  const bubble = chatLog.lastElementChild

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  let data = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop()

    for (const line of lines) {
      if (!line) continue
      const event = JSON.parse(line)

      if (event.chunk) {
        bubble.textContent += event.chunk
        chatLog.scrollTop = chatLog.scrollHeight
      } else if (event.done) {
        data = event
      }
    }
  }

  if (!bubble.textContent) {
    bubble.textContent = data.answer
  }

  renderSources(data.sources)
  history.push({ role: "user", content: question })
  history.push({ role: "assistant", content: data.answer })

  if (data.limit_reached) {
    input.placeholder = "به سقفِ سؤال‌ها رسیدی — صفحه رو رفرش کن"
  } else {
    input.disabled = false
    input.focus()
  }
})
