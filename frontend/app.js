let currentConversationId = null;
const API_BASE_URL = "http://127.0.0.1:8000";


function appendMessage(role, content) {
    const chatBox = document.getElementById("chat-box");
    const message = document.createElement("div");

    message.className = `message ${role}`;
    message.innerText = content;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function setActiveConversation() {
    document.querySelectorAll(".conversation-item").forEach(item => {
        item.classList.toggle(
            "active",
            Number(item.dataset.id) === currentConversationId
        );
    });
}


async function loadConversations() {

    const response = await fetch(
        `${API_BASE_URL}/conversations`
    );

    const result = await response.json();

    const list = document.getElementById(
        "conversation-list"
    );

    list.innerHTML = "";

    result.data.forEach(conversation => {

        const item = document.createElement("div");

        item.className = "conversation-item";
        item.dataset.id = conversation.id;

        item.innerText = conversation.title;

        item.onclick = () => {

            currentConversationId = conversation.id;
            document.getElementById("chat-box").innerHTML = "";
            setActiveConversation();

            console.log(
                "切换会话:",
                currentConversationId
            );
        };

        list.appendChild(item);
    });

    setActiveConversation();
}


async function createConversation() {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title: "新对话" }),
    });

    const result = await response.json();
    currentConversationId = result.id;

    document.getElementById("chat-box").innerHTML = "";
    await loadConversations();
}


async function sendMessage() {
    const input = document.getElementById("message-input");
    const text = input.value.trim();

    if (!text) {
        return;
    }

    input.value = "";
    appendMessage("user", text);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: text,
                conversation_id: currentConversationId,
            }),
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || "请求失败");
        }

        currentConversationId = result.conversation_id;
        appendMessage("assistant", result.answer);
        await loadConversations();
    } catch (error) {
        appendMessage("error", error.message);
    }
}


document.getElementById("new-chat-btn").addEventListener("click", createConversation);
document.getElementById("message-input").addEventListener("keydown", event => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

loadConversations();
