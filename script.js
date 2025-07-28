document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

  
    // Send on click
    sendBtn.addEventListener('click', handleSend);
  
    // Send on Enter
    userInput.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault(); // Prevent form submission
        handleSend();
      }
    });
  
    function handleSend() {
      const message = userInput.value.trim();
      if (!message) return;
  
      appendMessage('user', message);
      userInput.value = '';}
  
      // Show typing placeholder
      const typingId = appendMessage('Hello, Welcome to our site, if you need help simply reply to this message, we are online and ready to help.');
  
      // Send to backend
      fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
      }
    )
    
    }
)