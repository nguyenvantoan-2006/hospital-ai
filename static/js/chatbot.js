/**
 * static/js/chatbot.js — Floating AI Chatbot Widget for Hospital-AI (Clinova)
 * Tự động khởi tạo UI bong bóng chat nổi và kết nối API /api/ai/chatbot
 */

(function () {
  "use strict";

  // Khởi tạo Chatbot sau khi DOM đã tải
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initClinovaChatbot);
  } else {
    initClinovaChatbot();
  }

  function initClinovaChatbot() {
    if (document.getElementById("clinovaChatFab")) return;

    // 1. Chèn HTML Widget vào cuối Body
    const widgetHtml = `
      <!-- Nút tròn Chatbot nổi (FAB) -->
      <button id="clinovaChatFab" class="clinova-chat-fab" title="Trợ lý AI Clinova" aria-label="Mở Trợ lý AI Clinova">
        <i class="fa-solid fa-robot"></i>
        <span class="badge-online"></span>
        <span class="fab-tooltip">Trợ lý AI Clinova (24/7)</span>
      </button>

      <!-- Khung Cửa Sổ Chat -->
      <div id="clinovaChatWindow" class="clinova-chat-window">
        <!-- Header -->
        <div class="clinova-chat-header">
          <div class="header-info">
            <div class="bot-avatar">
              <i class="fa-solid fa-robot"></i>
            </div>
            <div class="bot-title">
              <h4>Trợ Lý AI Clinova</h4>
              <span>Trực tuyến 24/7</span>
            </div>
          </div>
          <div class="header-actions">
            <button id="btnCloseChat" title="Thu nhỏ"><i class="fa-solid fa-xmark"></i></button>
          </div>
        </div>

        <!-- Body / Tin nhắn -->
        <div id="clinovaChatBody" class="clinova-chat-body">
          <!-- Tin nhắn chào mừng mặc định -->
          <div class="chat-msg bot-msg">
            <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-bubble">
              <p>👋 <strong>Xin chào bạn!</strong></p>
              <p>Tôi là Trợ lý AI của <strong>Clinova Hospital</strong>. Tôi luôn sẵn sàng hỗ trợ bạn:</p>
              <ul>
                <li>Thời gian làm việc & địa chỉ</li>
                <li>Bảng giá khám các chuyên khoa</li>
                <li>Quy trình khám & BHYT</li>
                <li>Hướng dẫn đặt lịch trực tuyến</li>
              </ul>
              <div class="quick-chips-container mt-2">
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Giờ làm việc của phòng khám?')">🕒 Giờ làm việc</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Bảng giá khám chuyên khoa bao nhiêu?')">💰 Bảng giá khám</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Quy trình khám bệnh gồm những bước nào?')">📝 Quy trình khám</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Làm sao để đặt lịch khám online?')">📅 Cách đặt lịch</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer / Input -->
        <div class="clinova-chat-footer">
          <form id="clinovaChatForm" onsubmit="window.clinovaHandleSubmit(event)">
            <div class="chat-input-wrapper">
              <input type="text" id="clinovaChatInput" placeholder="Hỏi về giờ khám, bảng giá, thủ tục..." autocomplete="off" />
              <button type="submit" id="btnSendChat" title="Gửi câu hỏi"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
          </form>
          <div class="chat-disclaimer">
            <i class="fa-solid fa-shield-halved"></i> AI chỉ tư vấn hành chính, không chẩn đoán y khoa.
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML("beforeend", widgetHtml);

    // 2. Gắn sự kiện Mở/Đóng
    const fab = document.getElementById("clinovaChatFab");
    const win = document.getElementById("clinovaChatWindow");
    const btnClose = document.getElementById("btnCloseChat");
    const input = document.getElementById("clinovaChatInput");

    fab.addEventListener("click", () => {
      const isVisible = win.style.display === "flex";
      win.style.display = isVisible ? "none" : "flex";
      if (!isVisible) {
        setTimeout(() => input.focus(), 150);
      }
    });

    btnClose.addEventListener("click", () => {
      win.style.display = "none";
    });
  }

  // 3. Xử lý Gửi tin nhắn
  window.clinovaHandleSubmit = async function (e) {
    if (e) e.preventDefault();
    const input = document.getElementById("clinovaChatInput");
    const msg = (input.value || "").trim();
    if (!msg) return;

    input.value = "";
    await sendUserMessage(msg);
  };

  window.clinovaSendQuickMessage = async function (text) {
    await sendUserMessage(text);
  };

  async function sendUserMessage(message) {
    const chatBody = document.getElementById("clinovaChatBody");
    const btnSend = document.getElementById("btnSendChat");
    const input = document.getElementById("clinovaChatInput");

    // 1. Thêm tin nhắn của người dùng vào giao diện
    appendMessage("user", message);

    // 2. Thêm Typing indicator
    const typingId = showTypingIndicator();
    btnSend.disabled = true;
    input.disabled = true;

    try {
      // 3. Gọi API POST /api/ai/chatbot
      const res = await fetch("/api/ai/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
      });

      removeTypingIndicator(typingId);

      if (!res.ok) {
        throw new Error(`Lỗi kết nối (${res.status})`);
      }

      const data = await res.json();
      appendMessage("bot", data.reply);

    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage("bot", "⚠️ Xin lỗi, tôi đang gặp gián đoạn tạm thời. Bạn vui lòng liên hệ Hotline **1900 6868** hoặc thử lại sau nhé!");
    } finally {
      btnSend.disabled = false;
      input.disabled = false;
      input.focus();
    }
  }

  function appendMessage(sender, text) {
    const chatBody = document.getElementById("clinovaChatBody");
    const isBot = sender === "bot";

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${isBot ? "bot-msg" : "user-msg"}`;

    const formattedHtml = formatMarkdown(text);

    msgDiv.innerHTML = `
      ${isBot ? '<div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>' : ''}
      <div class="msg-bubble">
        ${formattedHtml}
      </div>
    `;

    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function showTypingIndicator() {
    const chatBody = document.getElementById("clinovaChatBody");
    const typingDiv = document.createElement("div");
    const id = "typing_" + Date.now();
    typingDiv.id = id;
    typingDiv.className = "chat-msg bot-msg";
    typingDiv.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="msg-bubble typing-bubble">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    chatBody.appendChild(typingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // Chuyển đổi Markdown cơ bản sang HTML an toàn
  function formatMarkdown(str) {
    if (!str) return "";
    let safe = str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // In đậm **text**
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // In nghiêng *text*
    safe = safe.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Bullet point: - item
    safe = safe.replace(/^- (.*)$/gim, "<li>$1</li>");
    if (safe.includes("<li>")) {
      safe = safe.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");
    }
    // Dòng mới \n -> <br>
    safe = safe.replace(/\n/g, "<br>");

    return safe;
  }
})();
