const chatbox = document.getElementById("chatbox");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const loader = document.getElementById("loader");

// Function to add a message to the chatbox
function appendMessage(text, sender) {
  const message = document.createElement("div");
  message.classList.add("message");
  message.classList.add(sender); // 'user' or 'bot'
  message.textContent = text;
  chatbox.appendChild(message);
  chatbox.scrollTop = chatbox.scrollHeight;
}

// Function to send the question to the backend
async function sendQuestion() {
  const question = userInput.value.trim();
  if (!question) return;

  appendMessage(question, "user");
  userInput.value = "";
  loader.style.display = "block";

  try {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
    });

    if (!response.ok) {
      throw new Error("Server error");
    }

    const data = await response.json();
    appendMessage(data.answer, "bot");
  } catch (error) {
    console.error(error);
    appendMessage("Sorry, I could not process your request.", "bot");
  } finally {
    loader.style.display = "none";
  }
}

// Event listeners
sendButton.addEventListener("click", sendQuestion);
userInput.addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    sendQuestion();
  }
});
