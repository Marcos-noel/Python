document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("send-btn");
  const userInput = document.getElementById("user-input");
  const chatbox = document.getElementById("chatbox");

  function appendMessage(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = sender + "-message";
    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = message;
    messageDiv.appendChild(bubble);
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function showTypingIndicator() {
    const typing = document.createElement("div");
    typing.className = "bot-message typing-indicator";
    typing.innerHTML = `<span></span><span></span><span></span>`;
    typing.id = "typing-indicator";
    chatbox.appendChild(typing);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function removeTypingIndicator() {
    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();
  }

  async function fetchBotResponse(userMessage) {
    showTypingIndicator();

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();
      removeTypingIndicator();
      appendMessage(data.response, "bot");
    } catch (error) {
      removeTypingIndicator();
      appendMessage("Sorry, something went wrong.", "bot");
      console.error("Chatbot error:", error);
    }
  }

  sendBtn.addEventListener("click", () => {
    const message = userInput.value.trim();
    if (message) {
      appendMessage(message, "user");
      userInput.value = "";
      fetchBotResponse(message);
    }
  });

  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendBtn.click();
    }
  });
});
