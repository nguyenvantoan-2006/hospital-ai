/**
 * static/js/chatbot.js — Floating AI Chatbot Widget for Hospital-AI (Clinova)
 * Tích hợp Voice-to-Text kiểm duyệt, Multimodal Vision/PDF đính kèm,
 * RAG CSDL nội bộ định hướng đi khám & chuẩn bị y tế không xuyên tạc.
 */

(function () {
  "use strict";

  // Khởi tạo Chatbot sau khi DOM đã tải
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initClinovaChatbot);
  } else {
    initClinovaChatbot();
  }

  // Biến lưu trữ tệp đính kèm hiện tại
  let currentAttachment = null;

  function initClinovaChatbot() {
    if (document.getElementById("clinovaChatFab")) return;

    // 1. Chèn HTML Widget vào cuối Body
    const widgetHtml = `
      <!-- Nút tròn Chatbot nổi (FAB) -->
      <button id="clinovaChatFab" class="clinova-chat-fab" title="Trợ lý AI Clinova" aria-label="Mở Trợ lý AI Clinova">
        <i class="fa-solid fa-robot"></i>
        <span class="badge-online"></span>
        <span class="fab-tooltip">Trợ lý AI Chuẩn Bị Khám (24/7)</span>
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
              <span>Định hướng chuẩn bị khám bệnh 24/7</span>
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
              <p>Tôi là <strong>Trợ lý AI của Clinova Hospital</strong>. Tôi hỗ trợ định hướng trước khi đi khám dựa trên <strong>dữ liệu chuẩn xác từ phòng khám</strong>:</p>
              <ul>
                <li>Gợi ý đúng chuyên khoa & bác sĩ phụ trách</li>
                <li>Dặn dò nhịn ăn xét nghiệm máu, nội soi, siêu âm</li>
                <li>Nhắc các giấy tờ cần mang (CCCD, BHYT, đơn cũ)</li>
                <li>Nhận diện ảnh đơn thuốc, kết quả xét nghiệm cũ</li>
              </ul>
              <div class="quick-chips-container mt-2">
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Xét nghiệm máu có cần nhịn ăn sáng không?')">🩸 Xét nghiệm máu</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Nội soi dạ dày cần chuẩn bị những gì?')">🔍 Nội soi dạ dày</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Siêu âm bụng có cần uống nhiều nước không?')">🩺 Siêu âm bụng</button>
                <button class="quick-chip" onclick="window.clinovaSendQuickMessage('Khám da liễu cần lưu ý gì trước khi đi?')">✨ Khám da liễu</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer / Input -->
        <div class="clinova-chat-footer">
          <!-- Thanh Preview tệp/hình ảnh đính kèm -->
          <div id="clinovaChatFilePreview" class="chat-file-preview-bar" style="display: none;">
            <div class="file-preview-content">
              <img id="clinovaFileThumb" class="file-preview-thumb" src="" alt="Thumbnail" style="display:none;" />
              <div id="clinovaFileIcon" class="file-preview-icon" style="display:none;"><i class="fa-solid fa-file-pdf"></i></div>
              <div class="file-preview-meta">
                <span id="clinovaFileName" class="file-preview-name"></span>
                <span id="clinovaFileSize" class="file-preview-size"></span>
              </div>
            </div>
            <button type="button" id="clinovaBtnRemoveFile" class="btn-remove-file" title="Xóa tệp đính kèm"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <form id="clinovaChatForm" onsubmit="window.clinovaHandleSubmit(event)">
            <div class="chat-input-wrapper">
              <!-- Nút đính kèm ảnh / file (Multimodal) -->
              <button type="button" id="clinovaBtnAttach" class="btn-chat-tool" title="Đính kèm ảnh xét nghiệm, đơn thuốc, thẻ BHYT, PDF..." aria-label="Đính kèm tệp">
                <i class="fa-solid fa-paperclip"></i>
              </button>
              <input type="file" id="clinovaFileInput" accept="image/*,application/pdf" style="display: none;" />

              <!-- Ô nhập liệu chính (Text từ phím hoặc Voice-to-Text được điền vào đây để người dùng kiểm duyệt) -->
              <input type="text" id="clinovaChatInput" placeholder="Hỏi triệu chứng, chuẩn bị nhịn ăn, giấy tờ..." autocomplete="off" />

              <!-- Nút thu âm giọng nói (Voice-to-Text) -->
              <button type="button" id="clinovaBtnVoice" class="btn-chat-tool" title="Nói để nhập liệu bằng giọng nói (Voice-to-Text)" aria-label="Nhập bằng giọng nói">
                <i class="fa-solid fa-microphone"></i>
              </button>

              <!-- Nút Gửi tin nhắn -->
              <button type="submit" id="btnSendChat" class="btn-chat-send" title="Gửi câu hỏi"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
          </form>
          <div class="chat-disclaimer">
            <i class="fa-solid fa-shield-halved"></i> Định hướng chuẩn bị khám từ CSDL Clinova, không thay thế bác sĩ.
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML("beforeend", widgetHtml);

    // 2. Gắn sự kiện Mở/Đóng Chatbot
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

    // 3. Khởi tạo Voice-to-Text với Web Speech API
    initVoiceRecognition(input);

    // 4. Khởi tạo File Attachment (Multimodal)
    initFileAttachment();
  }

  // ─── TÍNH NĂNG 1: VOICE-TO-TEXT VỚI BƯỚC KIỂM DUYỆT ──────────────────────────
  function initVoiceRecognition(inputEl) {
    const btnVoice = document.getElementById("clinovaBtnVoice");
    if (!btnVoice) return;

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRec) {
      btnVoice.addEventListener("click", () => {
        alert("Trình duyệt hiện tại chưa hỗ trợ nhận diện giọng nói Web Speech trực tiếp. Bạn vui lòng nhập câu hỏi bằng bàn phím nhé!");
      });
      return;
    }

    const recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "vi-VN"; // Mặc định Tiếng Việt, tự động nhận diện

    let isListening = false;

    recognition.onstart = () => {
      isListening = true;
      btnVoice.classList.add("recording-active");
      btnVoice.title = "Đang lắng nghe giọng nói... Bấm lại để dừng";
      inputEl.placeholder = "Đang nghe bạn nói... (Hãy nói rõ câu hỏi)";
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      // Điền lời nói vào ô input để người dùng đọc lại và kiểm duyệt lỗi chính tả
      const currentText = finalTranscript || interimTranscript;
      if (currentText) {
        inputEl.value = currentText;
      }
    };

    recognition.onerror = (err) => {
      console.warn("[Voice-to-Text Warning]", err.error);
      if (err.error === 'not-allowed') {
        alert("Trình duyệt chưa được cấp quyền Microphone. Vui lòng nhấn vào biểu tượng ổ khóa cạnh thanh địa chỉ web để 'Cho phép (Allow)' Microphone nhé!");
      }
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
      // Đặt con trỏ vào ô input để người dùng chủ động sửa chữa trước khi bấm Gửi
      inputEl.focus();
    };

    function stopListening() {
      isListening = false;
      btnVoice.classList.remove("recording-active");
      btnVoice.title = "Nói để nhập liệu bằng giọng nói (Voice-to-Text)";
      inputEl.placeholder = "Hỏi triệu chứng, chuẩn bị nhịn ăn, giấy tờ...";
    }

    btnVoice.addEventListener("click", () => {
      if (isListening) {
        recognition.stop();
      } else {
        try {
          recognition.start();
        } catch (e) {
          console.error("Speech start error:", e);
        }
      }
    });
  }

  // ─── TÍNH NĂNG 2: ĐÍNH KÈM HÌNH ẢNH / TÀI LIỆU (MULTIMODAL) ────────────────
  function initFileAttachment() {
    const btnAttach = document.getElementById("clinovaBtnAttach");
    const fileInput = document.getElementById("clinovaFileInput");
    const previewBar = document.getElementById("clinovaChatFilePreview");
    const fileThumb = document.getElementById("clinovaFileThumb");
    const fileIcon = document.getElementById("clinovaFileIcon");
    const fileName = document.getElementById("clinovaFileName");
    const fileSize = document.getElementById("clinovaFileSize");
    const btnRemove = document.getElementById("clinovaBtnRemoveFile");

    btnAttach.addEventListener("click", () => {
      fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;

      // Giới hạn dung lượng 10MB
      if (file.size > 10 * 1024 * 1024) {
        alert("Dung lượng tệp vượt quá 10MB. Vui lòng chọn tệp nhỏ hơn.");
        fileInput.value = "";
        return;
      }

      const reader = new FileReader();
      reader.onload = (uploadEvt) => {
        const dataUrl = uploadEvt.target.result;
        const isImage = file.type.startsWith("image/");
        const isPdf = file.type === "application/pdf";

        currentAttachment = {
          file: file,
          name: file.name,
          mimeType: file.type || (isImage ? "image/jpeg" : "application/pdf"),
          dataUrl: dataUrl,
          sizeFormatted: formatBytes(file.size),
          isImage: isImage,
          isPdf: isPdf
        };

        // Hiển thị preview bar
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);

        if (isImage) {
          fileThumb.src = dataUrl;
          fileThumb.style.display = "block";
          fileIcon.style.display = "none";
        } else {
          fileThumb.style.display = "none";
          fileIcon.style.display = "flex";
        }

        previewBar.style.display = "flex";
      };

      reader.readAsDataURL(file);
    });

    btnRemove.addEventListener("click", () => {
      clearAttachment();
    });
  }

  function clearAttachment() {
    currentAttachment = null;
    const fileInput = document.getElementById("clinovaFileInput");
    const previewBar = document.getElementById("clinovaChatFilePreview");
    if (fileInput) fileInput.value = "";
    if (previewBar) previewBar.style.display = "none";
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // ─── TÍNH NĂNG 3 & 4: GỬI TIN NHẮN & RAG ASSISTANT ────────────────────────
  window.clinovaHandleSubmit = async function (e) {
    if (e) e.preventDefault();
    const input = document.getElementById("clinovaChatInput");
    const msg = (input.value || "").trim();

    if (!msg && !currentAttachment) return;

    input.value = "";
    const attachedToSend = currentAttachment;
    clearAttachment();

    await sendUserMessage(msg, attachedToSend);
  };

  window.clinovaSendQuickMessage = async function (text) {
    await sendUserMessage(text, null);
  };

  async function sendUserMessage(message, attachment) {
    const chatBody = document.getElementById("clinovaChatBody");
    const btnSend = document.getElementById("btnSendChat");
    const input = document.getElementById("clinovaChatInput");

    const displayMsg = message || (attachment ? `Đã tải lên: ${attachment.name}` : "");

    // 1. Thêm tin nhắn người dùng kèm ảnh preview nếu có
    appendMessage("user", displayMsg, attachment);

    // 2. Thêm Typing indicator
    const typingId = showTypingIndicator();
    btnSend.disabled = true;
    input.disabled = true;

    try {
      // 3. Chuẩn bị Payload gọi API Backend
      const payload = {
        message: message || "Hãy xem hình ảnh / tài liệu đính kèm này và tư vấn chuyên khoa phù hợp cùng những dặn dò chuẩn bị trước khi khám giúp tôi.",
        image_base64: attachment ? attachment.dataUrl : null,
        image_mime_type: attachment ? attachment.mimeType : null,
        file_name: attachment ? attachment.name : null
      };

      // 4. Gửi yêu cầu sang API /api/ai/chatbot
      const res = await fetch("/api/ai/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      removeTypingIndicator(typingId);

      if (!res.ok) {
        throw new Error(`Lỗi kết nối máy chủ (${res.status})`);
      }

      const data = await res.json();
      appendMessage("bot", data.reply, null, data.specialties_recommended, data.suggested_actions);

    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage(
        "bot",
        "⚠️ Hệ thống AI đang tạm thời gián đoạn kết nối. Bạn vui lòng liên hệ Tổng đài **1900 6868** hoặc thử lại sau ít phút nhé!"
      );
    } finally {
      btnSend.disabled = false;
      input.disabled = false;
      input.focus();
    }
  }

  function appendMessage(sender, text, attachment, specialties, suggestedActions) {
    const chatBody = document.getElementById("clinovaChatBody");
    const isBot = sender === "bot";

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${isBot ? "bot-msg" : "user-msg"}`;

    const formattedHtml = formatMarkdown(text);

    let mediaHtml = "";
    if (attachment) {
      if (attachment.isImage) {
        mediaHtml = `
          <div class="attached-media-preview">
            <img src="${attachment.dataUrl}" alt="${attachment.name}" />
          </div>
        `;
      } else if (attachment.isPdf) {
        mediaHtml = `
          <div class="attached-doc-badge">
            <i class="fa-solid fa-file-pdf text-danger"></i>
            <span>${attachment.name} (${attachment.sizeFormatted})</span>
          </div>
        `;
      }
    }

    // Các nút bấm chuyển tiếp chuyên khoa (Direct Booking Chips)
    let bookingChipsHtml = "";
    if (isBot && specialties && specialties.length > 0) {
      bookingChipsHtml = `
        <div class="d-flex flex-wrap gap-2 mt-2 pt-2 border-top">
          ${specialties.map(spec => `
            <a href="dat_lich_online.html?khoa=${encodeURIComponent(spec)}" class="spec-booking-chip">
              <i class="fa-solid fa-calendar-check"></i> Đăng ký khám ${spec}
            </a>
          `).join("")}
        </div>
      `;
    }

    // Gợi ý câu hỏi tiếp theo
    let actionChipsHtml = "";
    if (isBot && suggestedActions && suggestedActions.length > 0) {
      actionChipsHtml = `
        <div class="quick-chips-container mt-2">
          ${suggestedActions.map(act => `
            <button class="quick-chip" onclick="window.clinovaSendQuickMessage('${act}')">${act}</button>
          `).join("")}
        </div>
      `;
    }

    msgDiv.innerHTML = `
      ${isBot ? '<div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>' : ''}
      <div class="msg-bubble">
        ${mediaHtml}
        ${formattedHtml ? `<div>${formattedHtml}</div>` : ''}
        ${bookingChipsHtml}
        ${actionChipsHtml}
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
    // Đường phân cách ---
    safe = safe.replace(/^---$/gm, "<hr style='margin: 8px 0; border: none; border-top: 1px dashed #cbd5e1;'>");
    // Bullet point: • hoặc -
    safe = safe.replace(/^[•\-] (.*)$/gim, "<li>$1</li>");
    if (safe.includes("<li>")) {
      safe = safe.replace(/(<li>.*<\/li>)/s, "<ul style='margin: 4px 0 0 16px; padding: 0;'>$1</ul>");
    }
    // Dòng mới \n -> <br>
    safe = safe.replace(/\n/g, "<br>");

    return safe;
  }
})();
