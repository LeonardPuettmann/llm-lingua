<script>
    import { onMount } from 'svelte';
  
    let messages = [];
    let inputMessage = '';
  
    const sendMessage = async () => {
        if (inputMessage.trim()) {
            messages.push({ text: inputMessage, sender: 'you' });
            const response = await fetch('http://localhost:8765/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: inputMessage })
            });
            const data = await response.json();
            messages.push({ text: data.answer, sender: 'LLM' });
            inputMessage = '';
        }
    };
</script>
  
<div class="chat-container">
    <div class="message-container">
      {#each messages as message (message.id)}
        <div class="message" class:sender={message.sender}>
          <div class="text">{message.text}</div>
        </div>
      {/each}
    </div>
    <div class="input-container">
      <input bind:value={inputMessage} on:keydown={(event) => event.key === 'Enter' && sendMessage()} />
      <button on:click={sendMessage}>Send</button>
    </div>
</div>
  
<style>
.chat-container {
    width: 300px;
    height: 400px;
    border: 1px solid black;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.message-container {
    flex-grow: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
}

.input-container {
    display: flex;
    gap: 10px;
    padding: 10px;
}

.message {
    align-self: flex-start;
    background-color: #ddd;
    padding: 5px;
    border-radius: 5px;
}

.message.sender {
    align-self: flex-end;
    background-color: #aaf;
}
</style>
