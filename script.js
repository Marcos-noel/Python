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
      const typingId = appendMessage('bot', 'Typing...');
  
      // Send to backend
      fetch('http://localhost:5000/ask', {
        method: 'POST',
      }
    )
    
    }
)