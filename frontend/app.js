let currentConversationId = null;

const API_BASE_URL = "http://127.0.0.1:8000";

const chatBox = document.getElementById("chat-box");
const conversationList = document.getElementById("conversation-list");
const conversationCount = document.getElementById("conversation-count");
const documentList = document.getElementById("document-list");
const documentCount = document.getElementById("document-count");
const documentInput = document.getElementById("document-input");
const uploadDocumentButton = document.getElementById("upload-document-btn");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const statusText = document.getElementById("status-text");
const activeTitle = document.getElementById("active-title");
const activeMeta = document.getElementById("active-meta");

const promptCards = [
    {
        title: "整理思路",
        text: "把一段零散想法变成清晰计划",
        prompt: "帮我把下面的想法整理成一个清晰的执行计划：",
    },
    {
        title: "润色表达",
        text: "让文案更自然、更有说服力",
        prompt: "请帮我润色下面这段文字，让它更自然、更有吸引力：",
    },
    {
        title: "拆解问题",
        text: "把复杂任务拆成可执行步骤",
        prompt: "请帮我拆解这个问题，并给出下一步行动建议：",
    },
];


function setStatus(text) {
    statusText.innerText = text;
}


function formatConversationTime(value) {
    if (!value) {
        return "刚刚";
    }

    const date = new Date(value.replace(" ", "T"));

    if (Number.isNaN(date.getTime())) {
        return "最近更新";
    }

    return new Intl.DateTimeFormat("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    }).format(date);
}


function updateActiveHeader(title, meta = "本地工作区") {
    activeTitle.innerText = title;
    activeMeta.innerText = meta;
}


function bindPromptCards() {
    document.querySelectorAll(".prompt-card").forEach(card => {
        card.addEventListener("click", () => {
            messageInput.value = card.dataset.prompt;
            autoResizeInput();
            messageInput.focus();
        });
    });
}


function renderEmptyState(title = "新的灵感从这里开始") {
    chatBox.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "empty-state";

    const visual = document.createElement("div");
    visual.className = "empty-visual";
    visual.setAttribute("aria-hidden", "true");

    const heading = document.createElement("h3");
    heading.innerText = title;

    const intro = document.createElement("p");
    intro.innerText = "把问题、想法或草稿交给 AI，让它陪你把下一步想清楚。";

    const grid = document.createElement("div");
    grid.className = "prompt-grid";

    promptCards.forEach(item => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "prompt-card";
        button.dataset.prompt = item.prompt;

        const cardTitle = document.createElement("strong");
        cardTitle.innerText = item.title;

        const cardText = document.createElement("span");
        cardText.innerText = item.text;

        button.appendChild(cardTitle);
        button.appendChild(cardText);
        grid.appendChild(button);
    });

    wrapper.appendChild(visual);
    wrapper.appendChild(heading);
    wrapper.appendChild(intro);
    wrapper.appendChild(grid);
    chatBox.appendChild(wrapper);

    bindPromptCards();
}


function removeEmptyState() {
    const emptyState = chatBox.querySelector(".empty-state");

    if (emptyState) {
        emptyState.remove();
    }
}


function createMessageElement(role) {
    removeEmptyState();

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else if (role === "error") {
        messageDiv.classList.add("ai-message", "error-message");
    } else {
        messageDiv.classList.add("ai-message");
    }

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");

    messageDiv.appendChild(contentDiv);
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    return {
        messageDiv,
        contentDiv,
    };
}


function appendMessage(role, content, sources = []) {
    const { contentDiv } = createMessageElement(role);
    contentDiv.innerText = content;

    appendSourcesToMessage(contentDiv, sources);

    chatBox.scrollTop = chatBox.scrollHeight;
}


function appendStreamingMessage() {
    removeTypingIndicator();

    const { messageDiv, contentDiv } = createMessageElement("assistant");
    const textSpan = document.createElement("span");
    textSpan.className = "stream-text";

    messageDiv.classList.add("streaming-message");
    contentDiv.appendChild(textSpan);

    return {
        messageDiv,
        contentDiv,
        textSpan,
        content: "",
    };
}


function appendSourcesToMessage(contentDiv, sources = []) {
    if (Array.isArray(sources) && sources.length > 0) {
        contentDiv.appendChild(renderSources(sources));
    }
}


function renderSources(sources) {
    const sourceList = document.createElement("div");
    sourceList.className = "message-sources";

    sources.forEach(source => {
        const item = document.createElement("div");
        item.className = "source-item";

        const title = document.createElement("div");
        title.className = "source-title";
        title.innerText = buildSourceTitle(source);

        const preview = document.createElement("div");
        preview.className = "source-preview";
        preview.innerText = source.preview || "";

        item.appendChild(title);
        item.appendChild(preview);
        sourceList.appendChild(item);
    });

    return sourceList;
}


function buildSourceTitle(source) {
    const page = source.page_number ? ` · 第 ${source.page_number} 页` : "";
    return `${source.filename || "文档"}${page} · 片段 ${(source.chunk_index || 0) + 1}`;
}


function appendTypingIndicator() {
    removeEmptyState();
    removeTypingIndicator();

    const messageDiv = document.createElement("div");
    messageDiv.id = "typing-indicator";
    messageDiv.className = "message ai-message typing-message";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const dots = document.createElement("span");
    dots.className = "typing-dots";
    dots.setAttribute("aria-label", "AI 正在回复");

    for (let index = 0; index < 3; index += 1) {
        dots.appendChild(document.createElement("span"));
    }

    contentDiv.appendChild(dots);
    messageDiv.appendChild(contentDiv);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function removeTypingIndicator() {
    const typing = document.getElementById("typing-indicator");

    if (typing) {
        typing.remove();
    }
}


function setActiveConversation() {
    document.querySelectorAll(".conversation-item").forEach(item => {
        item.classList.toggle(
            "active",
            Number(item.dataset.id) === currentConversationId
        );
    });
}


function renderConversationItem(conversation) {
    const item = document.createElement("div");
    item.className = "conversation-item";
    item.dataset.id = conversation.id;
    item.tabIndex = 0;
    item.setAttribute("role", "button");

    const textWrap = document.createElement("span");
    textWrap.className = "item-text";

    const title = document.createElement("span");
    title.className = "conversation-title";
    title.innerText = conversation.title || "新对话";

    const time = document.createElement("span");
    time.className = "conversation-time";
    time.innerText = formatConversationTime(conversation.created_at);

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-item-btn";
    deleteButton.type = "button";
    deleteButton.innerText = "×";
    deleteButton.title = "删除会话";
    deleteButton.setAttribute("aria-label", `删除会话 ${conversation.title || "新对话"}`);

    deleteButton.addEventListener("click", event => {
        event.stopPropagation();
        deleteConversation(conversation.id, conversation.title || "新对话");
    });

    textWrap.appendChild(title);
    textWrap.appendChild(time);
    item.appendChild(textWrap);
    item.appendChild(deleteButton);

    const selectConversation = () => {
        currentConversationId = conversation.id;
        updateActiveHeader(conversation.title || "新对话", "会话已选择");
        renderEmptyState(conversation.title || "继续这次对话");
        setActiveConversation();
    };

    item.addEventListener("click", selectConversation);
    item.addEventListener("keydown", event => {
        if (event.target !== item) {
            return;
        }

        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            selectConversation();
        }
    });

    return item;
}


function renderConversationEmpty(text) {
    const empty = document.createElement("div");
    empty.className = "conversation-empty";
    empty.innerText = text;
    conversationList.appendChild(empty);
}


async function deleteConversation(conversationId, title) {
    const confirmed = window.confirm(`确定删除会话“${title}”吗？`);

    if (!confirmed) {
        return;
    }

    setStatus("正在删除会话");

    try {
        const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
            method: "DELETE",
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "会话删除失败");
        }

        if (currentConversationId === conversationId) {
            currentConversationId = null;
            updateActiveHeader("新的灵感从这里开始", "本地工作区");
            renderEmptyState();
        }

        await loadConversations();
        setStatus("会话已删除");
    } catch (error) {
        setStatus("删除失败");
        appendMessage("error", error.message);
    }
}


function renderDocumentItem(documentItem) {
    const item = document.createElement("div");
    item.className = "document-item";

    const textWrap = document.createElement("span");
    textWrap.className = "item-text";

    const title = document.createElement("span");
    title.className = "document-title";
    title.innerText = documentItem.filename || "未命名文档";

    const meta = document.createElement("span");
    meta.className = "document-meta";
    meta.innerText = `${documentItem.chunk_count || 0} 个片段 · ${formatConversationTime(documentItem.created_at)}`;

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-item-btn";
    deleteButton.type = "button";
    deleteButton.innerText = "×";
    deleteButton.title = "删除文档";
    deleteButton.setAttribute("aria-label", `删除文档 ${documentItem.filename || "未命名文档"}`);

    deleteButton.addEventListener("click", () => {
        deleteDocument(documentItem.id, documentItem.filename || "未命名文档");
    });

    textWrap.appendChild(title);
    textWrap.appendChild(meta);
    item.appendChild(textWrap);
    item.appendChild(deleteButton);

    return item;
}


async function deleteDocument(documentId, filename) {
    const confirmed = window.confirm(`确定删除文档“${filename}”吗？`);

    if (!confirmed) {
        return;
    }

    setStatus("正在删除文档");

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
            method: "DELETE",
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "文档删除失败");
        }

        await loadDocuments();
        setStatus("文档已删除");
    } catch (error) {
        setStatus("删除失败");
        documentList.innerHTML = "";
        renderDocumentEmpty(error.message);
    }
}


function renderDocumentEmpty(text) {
    const empty = document.createElement("div");
    empty.className = "document-empty";
    empty.innerText = text;
    documentList.appendChild(empty);
}


async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/documents`);

        if (!response.ok) {
            throw new Error("文档列表加载失败");
        }

        const result = await response.json();
        const documents = Array.isArray(result.data) ? result.data : [];

        documentList.innerHTML = "";
        documentCount.innerText = documents.length;

        if (documents.length === 0) {
            renderDocumentEmpty("还没有文档");
        } else {
            documents.forEach(documentItem => {
                documentList.appendChild(renderDocumentItem(documentItem));
            });
        }
    } catch (error) {
        documentList.innerHTML = "";
        documentCount.innerText = "0";
        renderDocumentEmpty("文档库未连接");
    }
}


function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
            const result = String(reader.result || "");
            resolve(result.includes(",") ? result.split(",", 2)[1] : result);
        };

        reader.onerror = () => reject(new Error("文件读取失败"));
        reader.readAsDataURL(file);
    });
}


async function uploadDocument(file) {
    if (!file) {
        return;
    }

    uploadDocumentButton.disabled = true;
    setStatus("正在解析文档");

    try {
        const contentBase64 = await readFileAsBase64(file);
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                filename: file.name,
                content_type: file.type,
                content_base64: contentBase64,
            }),
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "文档上传失败");
        }

        setStatus(`已索引 ${result.chunk_count || 0} 个片段`);
        updateActiveHeader("文档库已更新", result.filename || "新文档");
        await loadDocuments();
    } catch (error) {
        documentList.innerHTML = "";
        renderDocumentEmpty(error.message);
        setStatus("文档上传失败");
    } finally {
        uploadDocumentButton.disabled = false;
        documentInput.value = "";
    }
}


async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations`);

        if (!response.ok) {
            throw new Error("会话列表加载失败");
        }

        const result = await response.json();
        const conversations = Array.isArray(result.data) ? result.data : [];

        conversationList.innerHTML = "";
        conversationCount.innerText = conversations.length;

        if (conversations.length === 0) {
            renderConversationEmpty("还没有会话");
        } else {
            conversations.forEach(conversation => {
                conversationList.appendChild(renderConversationItem(conversation));
            });
        }

        setActiveConversation();
        setStatus("准备就绪");
    } catch (error) {
        conversationList.innerHTML = "";
        conversationCount.innerText = "0";
        renderConversationEmpty("无法连接后端服务");
        setStatus("后端未连接");
    }
}


async function createConversation() {
    setStatus("正在创建");

    try {
        const response = await fetch(`${API_BASE_URL}/conversations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title: "新对话" }),
        });

        if (!response.ok) {
            throw new Error("新建会话失败");
        }

        const result = await response.json();
        currentConversationId = result.id;

        updateActiveHeader(result.title || "新对话", "新会话");
        renderEmptyState("新对话");
        await loadConversations();
    } catch (error) {
        appendMessage("error", error.message);
        setStatus("创建失败");
    }
}


function setSending(isSending) {
    sendButton.disabled = isSending;
    messageInput.disabled = isSending;

    if (isSending) {
        setStatus("AI 正在回复");
    }
}


async function sendMessage() {
    const text = messageInput.value.trim();

    if (!text || sendButton.disabled) {
        return;
    }

    messageInput.value = "";
    autoResizeInput();
    appendMessage("user", text);
    setSending(true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: text,
                conversation_id: currentConversationId,
            }),
        });

        if (!response.ok) {
            throw new Error(await readErrorMessage(response));
        }

        await consumeChatStream(response);
    } catch (error) {
        removeTypingIndicator();
        removeStreamingMessages();
        appendMessage("error", `发送失败：${error.message}`);
        setStatus("发送失败");
    } finally {
        setSending(false);
        messageInput.focus();
    }
}


async function readErrorMessage(response) {
    try {
        const result = await response.json();
        return result.detail || "请求失败";
    } catch (error) {
        return await response.text() || "请求失败";
    }
}


async function consumeChatStream(response) {
    if (!response.body) {
        throw new Error("当前浏览器不支持流式读取。");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let streamMessage = null;
    let streamSources = [];
    let streamDone = false;

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        buffer += decoder.decode(value, { stream: true });

        const events = extractSseEvents(buffer);
        buffer = events.remaining;

        for (const rawEvent of events.items) {
            const result = handleStreamEvent(rawEvent, streamMessage, streamSources);
            streamMessage = result.streamMessage;
            streamSources = result.streamSources;
            streamDone = streamDone || result.streamDone;
        }
    }

    if (buffer.trim()) {
        const result = handleStreamEvent(buffer, streamMessage, streamSources);
        streamMessage = result.streamMessage;
        streamSources = result.streamSources;
        streamDone = streamDone || result.streamDone;
    }

    if (!streamDone && streamMessage) {
        finishStreamingMessage(streamMessage, streamSources);
    }

    setStatus("准备就绪");
    await loadConversations();
}


function handleStreamEvent(rawEvent, streamMessage, streamSources) {
    const event = parseSseEvent(rawEvent);

    if (!event) {
        return {
            streamMessage,
            streamSources,
            streamDone: false,
        };
    }

    if (event.event === "start") {
        currentConversationId = event.data.conversation_id;
        streamSources = event.data.sources || [];
        streamMessage = appendStreamingMessage();
        updateActiveHeader(
            "正在对话",
            streamSources.length ? `命中 ${streamSources.length} 个片段` : "流式回复中"
        );
    } else if (event.event === "delta") {
        if (!streamMessage) {
            streamMessage = appendStreamingMessage();
        }

        streamMessage.content += event.data.content || "";
        streamMessage.textSpan.innerText = streamMessage.content;
        chatBox.scrollTop = chatBox.scrollHeight;
    } else if (event.event === "done") {
        currentConversationId = event.data.conversation_id || currentConversationId;
        streamSources = event.data.sources || streamSources;
        finishStreamingMessage(streamMessage, streamSources);

        return {
            streamMessage,
            streamSources,
            streamDone: true,
        };
    } else if (event.event === "error") {
        throw new Error(event.data.message || "流式回复失败");
    }

    return {
        streamMessage,
        streamSources,
        streamDone: false,
    };
}


function finishStreamingMessage(streamMessage, sources = []) {
    if (!streamMessage) {
        return;
    }

    streamMessage.messageDiv.classList.remove("streaming-message");

    if (!streamMessage.content.trim()) {
        streamMessage.textSpan.innerText = "暂无回复";
    }

    appendSourcesToMessage(streamMessage.contentDiv, sources);
    chatBox.scrollTop = chatBox.scrollHeight;
}


function removeStreamingMessages() {
    document.querySelectorAll(".streaming-message").forEach(message => {
        message.remove();
    });
}


function extractSseEvents(buffer) {
    const items = [];
    let remaining = buffer;

    while (true) {
        const match = remaining.match(/\r?\n\r?\n/);

        if (!match) {
            break;
        }

        items.push(remaining.slice(0, match.index));
        remaining = remaining.slice(match.index + match[0].length);
    }

    return {
        items,
        remaining,
    };
}


function parseSseEvent(rawEvent) {
    const lines = rawEvent.split(/\r?\n/);
    const dataLines = [];
    let eventName = "message";

    lines.forEach(line => {
        if (line.startsWith("event:")) {
            eventName = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
            dataLines.push(line.slice(5).trimStart());
        }
    });

    if (dataLines.length === 0) {
        return null;
    }

    return {
        event: eventName,
        data: JSON.parse(dataLines.join("\n")),
    };
}


function autoResizeInput() {
    messageInput.style.height = "auto";
    messageInput.style.height = `${messageInput.scrollHeight}px`;
}


document.getElementById("new-chat-btn").addEventListener("click", createConversation);
uploadDocumentButton.addEventListener("click", () => documentInput.click());
documentInput.addEventListener("change", event => {
    uploadDocument(event.target.files[0]);
});
sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("input", autoResizeInput);
messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

renderEmptyState();
loadConversations();
loadDocuments();
