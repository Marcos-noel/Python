document.addEventListener("DOMContentLoaded", function () {
  const sendButton = document.getElementById("sendButton");
  const inputField = document.getElementById("userInput");
  const chatBox = document.getElementById("chatBox");

  // Show user message
  function addUserMessage(message) {
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.innerHTML = `<div class="message-text">${message}</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Typewriter effect for bot response
  function addBotMessageTyped(text) {
    const botMsg = document.createElement("div");
    botMsg.className = "bot-message";

    const messageText = document.createElement("div");
    messageText.className = "message-text";
    botMsg.appendChild(messageText);

    const timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.textContent = new Date().toLocaleTimeString();
    botMsg.appendChild(timestamp);

    chatBox.appendChild(botMsg);
    chatBox.scrollTop = chatBox.scrollHeight;

    let index = 0;
    const speed = 25; // Typing speed in ms

    function type() {
      if (index < text.length) {
        messageText.innerHTML += text.charAt(index);
        index++;
        chatBox.scrollTop = chatBox.scrollHeight;
        setTimeout(type, speed);
      }
    }

    type();
  }

  // Typing indicator
  function showTypingIndicator() {
    const typing = document.createElement("div");
    typing.className = "bot-message typing";
    typing.innerHTML = `<div class="message-text"><i>KEPROBA Assistant is typing...</i></div>`;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;
    return typing;
  }

  // Send user message to server
  async function sendMessage() {
    const userInput = inputField.value.trim();
    if (!userInput) return;

    addUserMessage(userInput);
    inputField.value = "";

    const typingIndicator = showTypingIndicator();

    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userInput })
      });

      chatBox.removeChild(typingIndicator);

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      const reply = data.reply || "Sorry, I couldn't understand your request.";
      addBotMessageTyped(reply); // Use typewriter effect
    } catch (err) {
      chatBox.removeChild(typingIndicator);
      addBotMessageTyped("⚠️ Error: Could not connect to the assistant.");
    }
  }

  sendButton.addEventListener("click", sendMessage);
  inputField.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  const typewriter = document.getElementById('typewriter');
  const text = "This is a ChatGPT-like typing effect, simulating human typing with random delays and a blinking cursor. It also supports multiline text and ensures the cursor is displayed at the end of the last output character.";
  
  let index = 0;
  
  function type() {
      if (index < text.length) {
          typewriter.innerHTML = text.slice(0, index) + '<span class="blinking-cursor">|</span>';
          index++;
          setTimeout(type, Math.random() * 150 + 50);
      } else {
          typewriter.innerHTML = text.slice(0, index) + '<span class="blinking-cursor">|</span>';
      }
  }
  
  type();


});

