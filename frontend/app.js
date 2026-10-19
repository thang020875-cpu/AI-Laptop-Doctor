// =========================================================
// AI LAPTOP DOCTOR - FRONTEND
// Version: 1.2.0
// =========================================================


// =========================================================
// HELPERS
// =========================================================

function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent =
            value;
    }
}


function formatValue(
    value,
    suffix = ""
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "--";
    }

    return `${value}${suffix}`;
}


// =========================================================
// SYMPTOM SESSION
// =========================================================

// Lấy session hiện tại từ trình duyệt
let sessionId =
    localStorage.getItem(
        "ai_laptop_doctor_session_id"
    );


// =========================================================
// SCAN
// =========================================================

async function scanLaptop() {

    const button =
        document.getElementById(
            "scanButton"
        );

    button.disabled =
        true;

    button.textContent =
        "⏳ Đang kiểm tra...";


    setText(
        "healthStatus",
        "Đang kiểm tra"
    );


    try {

        const response =
            await fetch(
                "/api/scan",
                {
                    method:
                        "POST"
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "Scan failed"
            );
        }


        renderReport(
            data.report
        );


    } catch (error) {

        console.error(
            error
        );


        setText(
            "healthStatus",
            "Lỗi"
        );


        document.getElementById(
            "diagnosis"
        ).innerHTML = `
            <p>
                Không thể kiểm tra laptop.
            </p>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
        `;


    } finally {

        button.disabled =
            false;

        button.textContent =
            "🔍 Kiểm tra laptop";
    }
}


// =========================================================
// RENDER REPORT
// =========================================================

function renderReport(
    report
) {

    const hardware =
        report.hardware ||
        {};


    const cpu =
        hardware.cpu ||
        {};


    const memory =
        hardware.memory ||
        {};


    const disk =
        hardware.disk ||
        {};


    const temperature =
        hardware.temperature ||
        {};


    const cpuTemperature =
        temperature.cpu ||
        {};


    const gpuTemperature =
        temperature.gpu ||
        {};


    const battery =
        hardware.battery ||
        {};


    const batteries =
        battery.batteries ||
        [];


    // -----------------------------------------------------
    // BASIC VALUES
    // -----------------------------------------------------

    setText(
        "cpuUsage",
        formatValue(
            cpu.usage_percent,
            "%"
        )
    );


    setText(
        "ramUsage",
        formatValue(
            memory.usage_percent,
            "%"
        )
    );


    setText(
        "diskUsage",
        formatValue(
            disk.usage_percent,
            "%"
        )
    );


    setText(
        "cpuTemp",
        formatValue(
            cpuTemperature.package_c,
            "°C"
        )
    );


    setText(
        "gpuTemp",
        formatValue(
            gpuTemperature.core_c,
            "°C"
        )
    );


    let batteryLevel =
        "--";


    if (
        batteries.length > 0
    ) {

        batteryLevel =
            formatValue(
                batteries[0]
                    .charge_percent,
                "%"
            );
    }


    setText(
        "batteryLevel",
        batteryLevel
    );


    // -----------------------------------------------------
    // DIAGNOSIS
    // -----------------------------------------------------

    renderDiagnosis(
        report.diagnosis ||
        {}
    );
}


// =========================================================
// DIAGNOSIS UI (System Scan)
// =========================================================

function renderDiagnosis(
    diagnosis
) {

    const container =
        document.getElementById(
            "diagnosis"
        );


    const status =
        diagnosis.status ||
        "UNKNOWN";


    const issueCount =
        diagnosis.issue_count ||
        0;


    setText(
        "healthStatus",
        status
    );


    setText(
        "issueCount",
        `${issueCount} vấn đề`
    );


    let html = "";


    html += `
        <div class="diagnosis-status">
            ${escapeHtml(status)}
        </div>
    `;


    const issues =
        diagnosis.issues ||
        [];


    if (
        issues.length === 0
    ) {

        html += `
            <p>
                ✓ Không phát hiện vấn đề
                theo các rule hiện tại.
            </p>
        `;

    } else {

        for (
            const issue
            of issues
        ) {

            html += `
                <div class="issue">

                    <strong>
                        ${escapeHtml(
                            issue.title || ""
                        )}
                    </strong>

                    <p>
                        ${escapeHtml(
                            issue.reason || ""
                        )}
                    </p>

                    <p>
                        Severity:
                        ${escapeHtml(
                            issue.severity || ""
                        )}
                    </p>

                    <p>
                        Confidence:
                        ${escapeHtml(
                            issue.confidence || ""
                        )}
                    </p>

                </div>
            `;
        }
    }


    const recommendations =
        diagnosis.recommendations ||
        [];


    if (
        recommendations.length > 0
    ) {

        html += `
            <h3>
                💡 Khuyến nghị
            </h3>
        `;


        for (
            const recommendation
            of recommendations
        ) {

            html += `
                <div class="recommendation">
                    • ${escapeHtml(
                        recommendation
                    )}
                </div>
            `;
        }
    }


    container.innerHTML =
        html;
}


// =========================================================
// CHAT
// =========================================================

async function sendChat(
    optionalMessage
) {

    const input =
        document.getElementById(
            "chatInput"
        );


    // Ưu tiên message từ button (option), nếu không thì lấy từ input
    const message =
        (
            typeof optionalMessage === "string" &&
            optionalMessage.trim()
        )
            ? optionalMessage.trim()
            : (input ? input.value.trim() : "");


    if (!message) {

        return;
    }


    // -----------------------------------------------------
    // HIỂN THỊ TIN NHẮN USER
    // -----------------------------------------------------

    addChatMessage(
        "user",
        message
    );


    // Chỉ xóa input khi người dùng gõ (không xóa khi click option)
    if (
        input &&
        (
            typeof optionalMessage !== "string" ||
            !optionalMessage.trim()
        )
    ) {

        input.value =
            "";
    }


    // -----------------------------------------------------
    // HIỂN THỊ LOADING
    // -----------------------------------------------------

    addChatMessage(
        "ai",
        "Đang phân tích..."
    );


    try {

        // -------------------------------------------------
        // GỬI MESSAGE + SESSION ID
        // -------------------------------------------------

        const response =
            await fetch(
                "/api/chat",
                {

                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            message:
                                message,

                            session_id:
                                sessionId

                        })
                }
            );


        // -------------------------------------------------
        // KIỂM TRA HTTP ERROR
        // -------------------------------------------------

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        // -------------------------------------------------
        // XÓA "ĐANG PHÂN TÍCH..."
        // -------------------------------------------------

        removeLastAIMessage();


        // -------------------------------------------------
        // LƯU SESSION ID
        // -------------------------------------------------

        if (
            data.session_id
        ) {

            sessionId =
                data.session_id;


            localStorage.setItem(
                "ai_laptop_doctor_session_id",
                sessionId
            );
        }


        // -------------------------------------------------
        // HIỂN THỊ CÂU TRẢ LỜI AI (hỗ trợ structured Brain + Markdown)
        // -------------------------------------------------

        renderAIResponse(
            data
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        removeLastAIMessage();


        addChatMessage(
            "ai",
            "Không thể kết nối AI. Vui lòng kiểm tra Backend."
        );
    }
}


// =========================================================
// RENDER AI RESPONSE (Brain + Markdown + Options)
// =========================================================

function renderAIResponse(
    data
) {

    // data an toàn
    data =
        data ||
        {};


    const answer =
        data.answer ||
        "Không nhận được câu trả lời.";


    // Các field có thể có từ Backend (không tự tạo nếu thiếu)
    const status =
        data.status ||
        data.brain_status ||
        null;


    const causes =
        data.causes ||
        data.possible_causes ||
        data.top_causes ||
        [];


    const evidence =
        data.evidence ||
        data.evidences ||
        [];


    const nextStep =
        data.next_step ||
        data.nextStep ||
        null;


    const options =
        data.options ||
        (nextStep && nextStep.options) ||
        [];


    // Có dữ liệu Brain structured không?
    const hasBrainData =
        status ||
        (Array.isArray(causes) && causes.length > 0) ||
        (Array.isArray(evidence) && evidence.length > 0) ||
        nextStep;


    const chatBox =
        document.getElementById(
            "chatBox"
        );


    if (!chatBox) {

        return;
    }


    const div =
        document.createElement(
            "div"
        );


    // Class status nếu có
    let statusClass =
        "";


    if (status) {

        const s =
            String(status).toUpperCase();

        if (s === "CONFIRMED") {

            statusClass =
                " diagnosis-confirmed";

        } else if (s === "LIKELY") {

            statusClass =
                " diagnosis-likely";

        } else if (s === "POSSIBLE") {

            statusClass =
                " diagnosis-possible";

        } else if (s === "UNKNOWN") {

            statusClass =
                " diagnosis-unknown";
        }
    }


    div.className =
        `message ai${statusClass}`;


    let html = `
        <strong>
            AI Laptop Doctor
        </strong>
    `;


    // -------------------------------------------------
    // PHẦN BRAIN STRUCTURED (nếu Backend trả)
    // -------------------------------------------------

    if (hasBrainData) {

        html += `
            <div class="brain-block">
                <div class="brain-header">
                    🧠 Diagnostic Brain
                </div>
        `;


        if (status) {

            html += `
                <div class="brain-status">
                    ${escapeHtml(String(status))}
                </div>
            `;
        }


        // Causes
        if (
            Array.isArray(causes) &&
            causes.length > 0
        ) {

            html += `
                <div class="brain-section">
                    <strong>Nguyên nhân ưu tiên:</strong>
                    <ol class="brain-causes">
            `;


            for (
                let i = 0;
                i < causes.length;
                i++
            ) {

                const c =
                    causes[i] ||
                    {};


                const title =
                    c.title ||
                    c.name ||
                    c.cause ||
                    String(c);


                const score =
                    c.score !== undefined
                        ? c.score
                        : (c.confidence !== undefined ? c.confidence : null);


                html += `
                    <li>
                        ${escapeHtml(String(title))}
                        ${
                            score !== null
                                ? `<span class="brain-score">Score: ${escapeHtml(String(score))}</span>`
                                : ""
                        }
                    </li>
                `;
            }


            html += `
                    </ol>
                </div>
            `;
        }


        // Evidence
        if (
            Array.isArray(evidence) &&
            evidence.length > 0
        ) {

            html += `
                <div class="brain-section">
                    <strong>Evidence:</strong>
                    <ul class="brain-evidence">
            `;


            for (
                const e of evidence
            ) {

                const text =
                    typeof e === "string"
                        ? e
                        : (e.text || e.description || e.name || String(e));


                html += `
                    <li>✓ ${escapeHtml(String(text))}</li>
                `;
            }


            html += `
                    </ul>
                </div>
            `;
        }


        html += `
            </div>
        `;
    }


    // -------------------------------------------------
    // PHẦN ANSWER (Markdown)
    // -------------------------------------------------

    html += `
        <div class="ai-answer">
            ${renderMarkdown(answer)}
        </div>
    `;


    // -------------------------------------------------
    // NEXT STEP
    // -------------------------------------------------

    if (nextStep) {

        const nsTitle =
            nextStep.title ||
            nextStep.name ||
            "Bước tiếp theo";


        const nsDesc =
            nextStep.description ||
            nextStep.text ||
            nextStep.content ||
            "";


        html += `
            <div class="next-step-block">
                <div class="next-step-header">
                    🔧 Bước tiếp theo
                </div>
                <div class="next-step-title">
                    ${escapeHtml(String(nsTitle))}
                </div>
                <div class="next-step-desc">
                    ${renderMarkdown(String(nsDesc))}
                </div>
        `;


        // Options của next_step (nếu có)
        const nsOptions =
            nextStep.options ||
            [];


        if (
            Array.isArray(nsOptions) &&
            nsOptions.length > 0
        ) {

            html += `
                <div class="option-buttons">
            `;


            for (
                const opt of nsOptions
            ) {

                const label =
                    typeof opt === "string"
                        ? opt
                        : (opt.label || opt.text || opt.value || String(opt));


                // Escape cho attribute
                const safeLabel =
                    String(label)
                        .replace(/"/g, "&quot;")
                        .replace(/'/g, "&#39;");


                html += `
                    <button
                        type="button"
                        class="option-btn"
                        onclick="sendChat('${safeLabel}')"
                    >
                        ${escapeHtml(String(label))}
                    </button>
                `;
            }


            html += `
                </div>
            `;
        }


        html += `
            </div>
        `;
    }


    // -------------------------------------------------
    // OPTIONS (câu hỏi / verification) - nếu có ngoài next_step
    // -------------------------------------------------

    if (
        Array.isArray(options) &&
        options.length > 0 &&
        !nextStep
    ) {

        html += `
            <div class="option-buttons">
        `;


        for (
            const opt of options
        ) {

            const label =
                typeof opt === "string"
                    ? opt
                    : (opt.label || opt.text || opt.value || String(opt));


            const safeLabel =
                String(label)
                    .replace(/"/g, "&quot;")
                    .replace(/'/g, "&#39;");


            html += `
                <button
                    type="button"
                    class="option-btn"
                    onclick="sendChat('${safeLabel}')"
                >
                    ${escapeHtml(String(label))}
                </button>
            `;
        }


        html += `
            </div>
        `;
    }


    div.innerHTML =
        html;


    chatBox.appendChild(
        div
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// =========================================================
// START NEW DIAGNOSIS
// =========================================================

function newDiagnosis() {

    // Xóa phiên cũ
    sessionId = null;

    localStorage.removeItem(
        "ai_laptop_doctor_session_id"
    );


    addChatMessage(
        "ai",
        "Đã bắt đầu một phiên chẩn đoán mới. Bạn hãy mô tả triệu chứng của laptop."
    );
}


// =========================================================
// CLEAR SESSION
// =========================================================

function clearDiagnosisSession() {

    sessionId = null;

    localStorage.removeItem(
        "ai_laptop_doctor_session_id"
    );


    console.log(
        "AI Laptop Doctor: session đã được xóa."
    );
}


// =========================================================
// CHAT MESSAGE
// =========================================================

function addChatMessage(
    type,
    message
) {

    const chatBox =
        document.getElementById(
            "chatBox"
        );


    if (!chatBox) {

        return;
    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        `message ${type}`;


    const title =
        type === "ai"
            ? "AI Laptop Doctor"
            : "Bạn";


    // AI → Markdown an toàn
    // User → chỉ escape HTML
    const content =
        type === "ai"
            ? renderMarkdown(message)
            : escapeHtml(message);


    div.innerHTML = `
        <strong>
            ${escapeHtml(title)}
        </strong>

        <div class="message-content">
            ${content}
        </div>
    `;


    chatBox.appendChild(
        div
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// =========================================================
// REMOVE LAST AI MESSAGE
// =========================================================

function removeLastAIMessage() {

    const chatBox =
        document.getElementById(
            "chatBox"
        );


    if (!chatBox) {

        return;
    }


    const messages =
        chatBox.querySelectorAll(
            ".message.ai"
        );


    if (
        messages.length === 0
    ) {

        return;
    }


    const last =
        messages[
            messages.length - 1
        ];


    if (
        last.textContent.includes(
            "Đang phân tích"
        )
    ) {

        last.remove();
    }
}


// =========================================================
// ENTER
// =========================================================

function handleChatKey(
    event
) {

    if (
        event.key === "Enter"
    ) {

        event.preventDefault();

        sendChat();
    }
}


// =========================================================
// HTML SAFETY
// =========================================================

function escapeHtml(
    text
) {

    if (
        text === null ||
        text === undefined
    ) {

        return "";
    }


    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(text);


    return div.innerHTML;
}


// =========================================================
// LIGHTWEIGHT MARKDOWN RENDERER (an toàn chống XSS)
// =========================================================
// Hỗ trợ tối thiểu:
//   # ## ### heading
//   **bold**  *italic*  `code`
//   - bullet list
//   1. numbered list
//   > blockquote
// Luôn escape HTML trước → không bao giờ render raw HTML từ AI

function renderMarkdown(
    text
) {

    if (
        text === null ||
        text === undefined
    ) {

        return "";
    }


    // 1. Escape toàn bộ trước (chống XSS)
    let html =
        escapeHtml(
            String(text)
        );


    // 2. Xử lý theo dòng để hỗ trợ list / heading / quote tốt hơn
    const lines =
        html.split(
            "\n"
        );


    const result = [];

    let inUl = false;

    let inOl = false;

    let inBlockquote = false;


    function closeLists() {

        if (inUl) {

            result.push("</ul>");

            inUl = false;
        }

        if (inOl) {

            result.push("</ol>");

            inOl = false;
        }
    }


    function closeBlockquote() {

        if (inBlockquote) {

            result.push("</blockquote>");

            inBlockquote = false;
        }
    }


    for (
        let i = 0;
        i < lines.length;
        i++
    ) {

        let line =
            lines[i];


        // Heading ###
        if (
            /^###\s+/.test(line)
        ) {

            closeLists();

            closeBlockquote();

            result.push(
                "<h3>" +
                line.replace(
                    /^###\s+/,
                    ""
                ) +
                "</h3>"
            );

            continue;
        }


        // Heading ##
        if (
            /^##\s+/.test(line)
        ) {

            closeLists();

            closeBlockquote();

            result.push(
                "<h2>" +
                line.replace(
                    /^##\s+/,
                    ""
                ) +
                "</h2>"
            );

            continue;
        }


        // Heading #
        if (
            /^#\s+/.test(line)
        ) {

            closeLists();

            closeBlockquote();

            result.push(
                "<h1>" +
                line.replace(
                    /^#\s+/,
                    ""
                ) +
                "</h1>"
            );

            continue;
        }


        // Blockquote >
        if (
            /^&gt;\s?/.test(line)
        ) {

            closeLists();

            if (!inBlockquote) {

                result.push("<blockquote>");

                inBlockquote = true;
            }

            result.push(
                line.replace(
                    /^&gt;\s?/,
                    ""
                )
            );

            continue;
        }


        // Bullet list - hoặc *
        if (
            /^[-*]\s+/.test(line)
        ) {

            closeBlockquote();

            if (inOl) {

                result.push("</ol>");

                inOl = false;
            }

            if (!inUl) {

                result.push("<ul>");

                inUl = true;
            }

            result.push(
                "<li>" +
                line.replace(
                    /^[-*]\s+/,
                    ""
                ) +
                "</li>"
            );

            continue;
        }


        // Numbered list 1. 2. ...
        if (
            /^\d+\.\s+/.test(line)
        ) {

            closeBlockquote();

            if (inUl) {

                result.push("</ul>");

                inUl = false;
            }

            if (!inOl) {

                result.push("<ol>");

                inOl = true;
            }

            result.push(
                "<li>" +
                line.replace(
                    /^\d+\.\s+/,
                    ""
                ) +
                "</li>"
            );

            continue;
        }


        // Dòng trống → đóng list / quote + thêm khoảng cách
        if (
            line.trim() === ""
        ) {

            closeLists();

            closeBlockquote();

            result.push("<br>");

            continue;
        }


        // Dòng thường
        closeLists();

        closeBlockquote();

        result.push(
            "<p>" +
            line +
            "</p>"
        );
    }


    // Đóng hết nếu còn mở
    closeLists();

    closeBlockquote();


    html =
        result.join(
            "\n"
        );


    // 3. Inline styles (sau khi xử lý dòng)
    // Bold **text**
    html =
        html.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    // Italic *text* (không đụng ** đã xử lý)
    html =
        html.replace(
            /\*(.*?)\*/g,
            "<em>$1</em>"
        );


    // Inline code `code`
    html =
        html.replace(
            /`(.*?)`/g,
            "<code>$1</code>"
        );


    return html;
}


// =========================================================
// INITIALIZE
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "AI Laptop Doctor Frontend 1.2.0"
        );


        if (sessionId) {

            console.log(
                "Symptom session:",
                sessionId
            );
        }
    }
);