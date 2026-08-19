/* =========================================================
   AVTAR AI — APPLICATION LOGIC
   Frontend simulation
   Backend connection will be added after UI testing
========================================================= */


/* =========================================================
   STATE
========================================================= */

const state = {
    user: {
        name: "",
        gender: "",
        role: "student",
        userId: ""
    },

    messages: [],

    history: [],

    conversations: [],

    activeConversationId: "",

    selectedGender: "",

    currentPage: "dashboard",

    isListening: false,

    voiceEnabled: false,

    voiceInput: null,

    voiceContainer: null,

    theme: "midnight",

    accent: "purple"
};


/* =========================================================
   ELEMENTS
========================================================= */

const profileScreen =
    document.getElementById("profileScreen");

const dashboardScreen =
    document.getElementById("dashboardScreen");

const nameInput =
    document.getElementById("nameInput");

const roleInput =
    document.getElementById("roleInput");

const userIdInput =
    document.getElementById("userIdInput");

const continueBtn =
    document.getElementById("continueBtn");

const profileError =
    document.getElementById("profileError");

const genderButtons =
    document.querySelectorAll(".gender-btn");

const sidebarName =
    document.getElementById("sidebarName");

const sidebarRole =
    document.getElementById("sidebarRole");

const sidebarId =
    document.getElementById("sidebarId");

const sidebarAvatar =
    document.getElementById("sidebarAvatar");

const topAvatar =
    document.getElementById("topAvatar");

const welcomeName =
    document.getElementById("welcomeName");

const profileName =
    document.getElementById("profileName");

const profileGender =
    document.getElementById("profileGender");

const profileRole =
    document.getElementById("profileRole");

const profileId =
    document.getElementById("profileId");

const profilePageAvatar =
    document.getElementById("profilePageAvatar");

const messages =
    document.getElementById("messages");

const messageInput =
    document.getElementById("messageInput");

const sendBtn =
    document.getElementById("sendBtn");

const micBtn =
    document.getElementById("micBtn");

const fullMessages =
    document.getElementById("fullMessages");

const fullMessageInput =
    document.getElementById(
        "fullMessageInput"
    );

const fullSendBtn =
    document.getElementById(
        "fullSendBtn"
    );

const fullMicBtn =
    document.getElementById(
        "fullMicBtn"
    );

const fullTtsToggleBtn =
    document.getElementById(
        "fullTtsToggleBtn"
    );

const historyList =
    document.getElementById(
        "historyList"
    );

const newChatBtn =
    document.getElementById(
        "newChatBtn"
    );

const navButtons =
    document.querySelectorAll(
        ".nav-btn"
    );

const pages = {
    dashboard:
        document.getElementById(
            "dashboardPage"
        ),

    chat:
        document.getElementById(
            "chatPage"
        ),

    history:
        document.getElementById(
            "historyPage"
        ),

    profile:
        document.getElementById(
            "profilePage"
        ),

    settings:
        document.getElementById(
            "settingsPage"
        )
};

const pageTitle =
    document.getElementById(
        "pageTitle"
    );

const menuBtn =
    document.getElementById(
        "menuBtn"
    );

const sidebar =
    document.getElementById(
        "sidebar"
    );

const logoutBtn =
    document.getElementById(
        "logoutBtn"
    );

const themeBtn =
    document.getElementById(
        "themeBtn"
    );

const openThemeBtn =
    document.getElementById(
        "openThemeBtn"
    );

const themeModal =
    document.getElementById(
        "themeModal"
    );

const closeTheme =
    document.getElementById(
        "closeTheme"
    );

const themeChoices =
    document.querySelectorAll(
        ".theme-choice"
    );

const accentButtons =
    document.querySelectorAll(
        ".accent"
    );

const voiceModal =
    document.getElementById(
        "voiceModal"
    );

const stopVoice =
    document.getElementById(
        "stopVoice"
    );

const voiceSettingBtn =
    document.getElementById(
        "voiceSettingBtn"
    );


/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);


function initialize() {

    loadUser();

    loadTheme();

    setupGender();

    setupProfile();

    updateUserIdHint();

    setupNavigation();

    setupChat();

    setupFullChat();

    setupConversationControls();

    setupSidebar();

    setupTheme();

    setupVoice();

    setupLogout();

}


/* =========================================================
   PROFILE
========================================================= */

function setupGender() {

    genderButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                genderButtons.forEach(
                    item => {

                        item.classList.remove(
                            "selected"
                        );

                    }
                );


                button.classList.add(
                    "selected"
                );


                state.selectedGender =
                    button.dataset.gender;


                clearError();

            }
        );

    });

}


function setupProfile() {

    continueBtn.addEventListener(
        "click",
        createProfile
    );


    nameInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                createProfile();

            }

        }
    );


    userIdInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                createProfile();

            }

        }
    );

    roleInput.addEventListener(
        "change",
        updateUserIdHint
    );

}


function createProfile() {

    const name =
        nameInput.value.trim();

    const role =
        roleInput.value;

    const userId =
        userIdInput.value.trim();


    if (!name) {

        showError(
            "Please enter your name."
        );

        nameInput.focus();

        return;

    }


    if (!state.selectedGender) {

        showError(
            "Please select your gender."
        );

        return;

    }


    if (!userId) {

        showError(
            "Please enter your roll number."
        );

        userIdInput.focus();

        return;

    }


    state.user = {

        name: name,

        gender:
            state.selectedGender,

        role: role,

        userId: userId

    };


    saveUser();

    updateUserUI();

    loadConversation();

    transitionToDashboard();

}


function updateUserIdHint() {

    const role = roleInput.value;

    const hints = {
        student: ["Roll Number", "Enter your roll number (for example, 101)"],
        parent: ["Parent ID", "Enter your parent ID (for example, P001)"],
        teacher: ["Teacher ID", "Enter your teacher ID (for example, T001)"],
        principal: ["Principal ID", "Enter your principal ID (for example, PR001)"]
    };

    const [label, placeholder] = hints[role];
    userIdInput.previousElementSibling.textContent = label;
    userIdInput.placeholder = placeholder;

}


function showError(message) {

    profileError.textContent =
        message;

}


function clearError() {

    profileError.textContent =
        "";

}


function saveUser() {

    localStorage.setItem(
        "avtarUser",
        JSON.stringify(
            state.user
        )
    );

}


function loadUser() {

    const saved =
        localStorage.getItem(
            "avtarUser"
        );


    if (!saved) {

        return;

    }


    try {

        const user =
            JSON.parse(saved);


        if (
            !user.name ||
            !user.userId
        ) {

            return;

        }

        state.user =
            user;

        state.selectedGender =
            user.gender;

        // A saved profile should reopen directly in the active chat.
        nameInput.value = user.name;
        roleInput.value = user.role;
        userIdInput.value = user.userId;

        genderButtons.forEach(
            button => button.classList.toggle(
                "selected",
                button.dataset.gender === user.gender
            )
        );

        updateUserUI();
        loadConversation();
        transitionToDashboard(false);
        showPage("chat");

    } catch (error) {

        console.error(
            "Unable to load saved profile:",
            error
        );

    }

}


function updateUserUI() {

    const user =
        state.user;


    const firstName =
        user.name
            .split(" ")[0];


    const initial =
        user.name
            .charAt(0)
            .toUpperCase();


    sidebarName.textContent =
        user.name;

    sidebarRole.textContent =
        capitalize(
            user.role
        );

    sidebarId.textContent =
        user.userId;


    sidebarAvatar.textContent =
        initial;

    topAvatar.textContent =
        initial;


    welcomeName.textContent =
        firstName || "there";


    profileName.textContent =
        user.name;

    profileGender.textContent =
        capitalize(
            user.gender
        );

    profileRole.textContent =
        capitalize(
            user.role
        );

    profileId.textContent =
        user.userId;


    profilePageAvatar.textContent =
        initial;

}


function transitionToDashboard(
    animate = true
) {

    if (animate) {

        profileScreen.style.opacity =
            "0";

        profileScreen.style.transform =
            "scale(.98)";

        profileScreen.style.transition =
            "opacity .35s ease, transform .35s ease";


        setTimeout(
            () => {

                profileScreen.classList.add(
                    "hidden"
                );

                dashboardScreen.classList.remove(
                    "hidden"
                );

                resetPageScroll();

                showPage("dashboard");

                profileScreen.style.opacity =
                    "";

                profileScreen.style.transform =
                    "";

            },
            350
        );

    } else {

        profileScreen.classList.add(
            "hidden"
        );

        dashboardScreen.classList.remove(
            "hidden"
        );

        resetPageScroll();

        showPage("dashboard");

    }

}


function resetPageScroll() {

    window.scrollTo(0, 0);

    // Browsers can restore a prior scroll position after the saved profile
    // switches directly to the dashboard during page load.
    requestAnimationFrame(
        () => window.scrollTo(0, 0)
    );

    setTimeout(
        () => window.scrollTo(0, 0),
        100
    );

}


/* =========================================================
   NAVIGATION
========================================================= */

function setupNavigation() {

    navButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const page =
                    button.dataset.page;


                showPage(page);


                sidebar.classList.remove(
                    "open"
                );

                dashboardScreen.classList.remove(
                    "sidebar-open"
                );

            }
        );

    });

}


function showPage(pageName) {

    Object.values(pages).forEach(
        page => {

            page.classList.add(
                "hidden"
            );

        }
    );


    navButtons.forEach(button => {

        button.classList.remove(
            "active"
        );

    });


    if (!pages[pageName]) {

        return;

    }


    pages[pageName].classList.remove(
        "hidden"
    );


    const activeButton =
        document.querySelector(
            `.nav-btn[data-page="${pageName}"]`
        );


    if (activeButton) {

        activeButton.classList.add(
            "active"
        );

    }


    const titles = {

        dashboard:
            "AVTAR AI",

        chat:
            "AI Chat",

        history:
            "Conversation History",

        profile:
            "My Profile",

        settings:
            "Settings"

    };


    pageTitle.textContent =
        titles[pageName];


    state.currentPage =
        pageName;


    if (
        pageName === "history"
    ) {

        renderHistory();

    }

}


/* =========================================================
   SIDEBAR
========================================================= */

function setupSidebar() {

    menuBtn.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "open"
            );

            dashboardScreen.classList.toggle(
                "sidebar-open",
                sidebar.classList.contains("open")
            );

        }
    );

}


/* =========================================================
   CHAT
========================================================= */

function setupChat() {

    sendBtn.addEventListener(
        "click",
        () => {

            sendChatMessage(
                messageInput,
                messages
            );

        }
    );


    messageInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                sendChatMessage(
                    messageInput,
                    messages
                );

            }

        }
    );


    addInitialMessage();

}


function addInitialMessage() {

    if (state.history.length > 0) {

        renderConversation();

        return;

    }


    const firstName =
        state.user.name
            ? state.user.name.split(" ")[0]
            : "there";


    addSharedMessage(
        `Hello ${firstName}! 👋 How can I assist you today?`,
        "ai"
    );

}


function sendChatMessage(
    input,
    container
) {

    const text =
        input.value.trim();


    if (!text) {

        return;

    }


    addSharedMessage(
        text,
        "user"
    );


    input.value = "";


    saveConversation(
        text,
        "user"
    );


    showTyping(
        container
    );


    setTimeout(
        () => {

            removeTyping(
                container
            );


            const response =
                generateResponse(
                    text
                );


            addMessage(
                response,
                "ai",
                container
            );


            saveConversation(
                response,
                "ai"
            );


        },
        650
    );

}


function addMessage(
    text,
    sender,
    container,
    timestamp = new Date().toISOString()
) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        `message ${sender}`;


    wrapper.textContent =
        text;


    const time =
        document.createElement(
            "span"
        );


    time.className =
        "message-time";


    time.textContent =
        formatMessageTime(timestamp);


    wrapper.appendChild(
        time
    );


    container.appendChild(
        wrapper
    );


    container.scrollTop =
        container.scrollHeight;

}


function showTyping(container) {

    const typing =
        document.createElement(
            "div"
        );


    typing.id =
        "typingIndicator";


    typing.className =
        "message ai";


    typing.innerHTML =
        "AVTAR is thinking <span class='typing-dots'>•••</span>";


    container.appendChild(
        typing
    );


    container.scrollTop =
        container.scrollHeight;

}


function removeTyping(container) {

    const typing =
        document.getElementById(
            "typingIndicator"
        );


    if (typing) {

        typing.remove();

    }

}


/* =========================================================
   AI SIMULATION
========================================================= */

function generateResponse(text) {

    const query =
        text.toLowerCase();


    if (
        query.includes("hello") ||
        query.includes("hi") ||
        query.includes("hey")
    ) {

        return (
            `Hello ${getFirstName()}! 👋 ` +
            `I'm AVTAR AI. What can I help you with?`
        );

    }


    if (
        query.includes("attendance")
    ) {

        return (
            "Sure! I can help you with attendance. " +
            "In the connected school system, " +
            "I'll retrieve the latest attendance record for you."
        );

    }


    if (
        query.includes("class")
    ) {

        return (
            "I can check your current class information. " +
            "Once the backend is connected, " +
            "I'll retrieve the exact class record."
        );

    }


    if (
        query.includes("teacher")
    ) {

        return (
            "Of course. I can help you with your teacher-related request " +
            "or prepare a request to contact the appropriate teacher."
        );

    }


    if (
        query.includes("parent")
    ) {

        return (
            "I can help with parent-related school information " +
            "and authorized requests."
        );

    }


    if (
        query.includes("thank")
    ) {

        return (
            "You're very welcome! 😊 " +
            "I'm always here to help."
        );

    }


    return (
        "I understand. I'm ready to help with your school-related request. " +
        "My live school-data connection will be connected to the backend next."
    );

}


/* =========================================================
   FULL CHAT PAGE
========================================================= */
async function sendChatMessage(
    input,
    container
) {
    const text = input.value.trim();


    if (!text) {
        return;
    }


    addSharedMessage(
        text,
        "user"
    );


    input.value = "";


    showSharedTyping();


    try {
        const previousMessages = state.history
            .slice(0, -1)
            .slice(-10)
            .map(
                item => `${item.sender}: ${item.text}`
            )
            .join("\n");


        const requestMessage = previousMessages
            ? `Previous conversation:\n${previousMessages}\n\nNew user message: ${text}`
            : text;

        // Live Server runs the frontend on port 5500, while FastAPI runs on
        // port 8000. In deployment, both are served from the same origin.
        const apiBaseUrl = window.location.port === "5500"
            ? "http://127.0.0.1:8000"
            : window.location.origin;

        const response = await fetch(
            `${apiBaseUrl}/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: requestMessage,
                    role: state.user.role,
                    user_id: state.user.userId
                })
            }
        );


        const data = await response.json();


        removeSharedTyping();


        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Backend request failed"
            );
        }


        addSharedMessage(
            data.response,
            "ai"
        );


        // Text-to-Speech
        speakText(data.response);


    } catch (error) {


        removeSharedTyping();


        // Keep the chat usable if the backend is restarting or unavailable.
        const fallbackResponse = generateResponse(text);

        addSharedMessage(
            fallbackResponse,
            "ai"
        );

        speakText(fallbackResponse);
    }
}
/* =========================================================
   VOICE
========================================================= */

function setupVoice() {

    micBtn.addEventListener(
        "click",
        () => toggleVoice(messageInput, messages)
    );


    stopVoice.addEventListener(
        "click",
        stopListening
    );


    [voiceSettingBtn, ttsToggleBtn, fullTtsToggleBtn].forEach(
        button => button?.addEventListener(
            "click",
            () => setVoiceEnabled(!state.voiceEnabled)
        )
    );

    setVoiceEnabled(
        localStorage.getItem("avtarVoiceEnabled") === "true"
    );

}


function setVoiceEnabled(enabled) {

    state.voiceEnabled = enabled;

    voiceSettingBtn.textContent = enabled ? "ON" : "OFF";
    voiceSettingBtn.classList.toggle("active", enabled);

    [ttsToggleBtn, fullTtsToggleBtn].forEach(button => {
        if (!button) return;
        button.textContent = enabled ? "🔊 Voice ON" : "🔇 Voice OFF";
        button.classList.toggle("active", enabled);
    });

    localStorage.setItem("avtarVoiceEnabled", String(enabled));

    if (!enabled) {
        window.speechSynthesis.cancel();
        stopListening();
    }

}

function toggleVoice(input = messageInput, container = messages) {

    if (!state.voiceEnabled) {
        return;
    }

    if (state.isListening) {
        stopListening();
    } else {
        state.voiceInput = input;
        state.voiceContainer = container;
        startListening();
    }
}


function startListening() {

    state.isListening =
        true;

    micBtn.classList.add(
        "recording"
    );

    fullMicBtn?.classList.add("recording");

    voiceModal.classList.remove(
        "hidden"
    );

    /*
       Browser speech recognition
       simulation / enhancement.

       If supported, the browser will
       listen to the microphone.
    */

    if (
        "webkitSpeechRecognition"
        in window
    ) {

        startBrowserSpeech();

    }

}
function stopListening() {

    state.isListening =
        false;


    micBtn.classList.remove(
        "recording"
    );

    fullMicBtn?.classList.remove("recording");


    voiceModal.classList.add(
        "hidden"
    );


    if (
        window.avtarRecognition
    ) {

        window.avtarRecognition.stop();

        window.avtarRecognition =
            null;

    }

}


function startBrowserSpeech() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        return;

    }


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-IN";


    recognition.interimResults =
        false;


    recognition.continuous =
        false;


    recognition.onresult =
        event => {

            const transcript =
                event
                    .results[0][0]
                    .transcript;


            const input = state.voiceInput || messageInput;
            const container = state.voiceContainer || messages;

            input.value = transcript;


            stopListening();


            sendChatMessage(
                input,
                container
            );

        };


    recognition.onerror =
        error => {

            console.log(
                "Voice recognition:",
                error
            );

            stopListening();

        };


    recognition.onend =
        () => {

            if (
                state.isListening
            ) {

                stopListening();

            }

        };


    window.avtarRecognition =
        recognition;


    recognition.start();

}


/* =========================================================
   THEME
========================================================= */

function setupTheme() {

    themeBtn.addEventListener(
        "click",
        openThemeModal
    );


    openThemeBtn.addEventListener(
        "click",
        openThemeModal
    );


    closeTheme.addEventListener(
        "click",
        closeThemeModal
    );


    themeModal.addEventListener(
        "click",
        event => {

            if (
                event.target ===
                themeModal
            ) {

                closeThemeModal();

            }

        }
    );


    themeChoices.forEach(
        choice => {

            choice.addEventListener(
                "click",
                () => {

                    const theme =
                        choice.dataset.theme;


                    changeTheme(
                        theme
                    );

                }
            );

        }
    );


    accentButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const accent =
                        button.dataset.accent;


                    changeAccent(
                        accent
                    );

                }
            );

        }
    );

}


function openThemeModal() {

    themeModal.classList.remove(
        "hidden"
    );

}


function closeThemeModal() {

    themeModal.classList.add(
        "hidden"
    );

}


function changeTheme(theme) {

    state.theme =
        theme;


    document.body.classList.remove(
        "theme-midnight",
        "theme-ocean",
        "theme-forest",
        "theme-sunset",
        "theme-rose"
    );


    if (
        theme !== "midnight"
    ) {

        document.body.classList.add(
            `theme-${theme}`
        );

    }


    themeChoices.forEach(
        choice => {

            choice.classList.toggle(
                "active",
                choice.dataset.theme === theme
            );

        }
    );


    localStorage.setItem(
        "avtarTheme",
        theme
    );

}


function changeAccent(accent) {

    state.accent =
        accent;


    document.body.classList.remove(
        "accent-blue",
        "accent-cyan",
        "accent-green",
        "accent-orange",
        "accent-pink"
    );


    if (
        accent !== "purple"
    ) {

        document.body.classList.add(
            `accent-${accent}`
        );

    }


    accentButtons.forEach(
        button => {

            button.classList.toggle(
                "active",
                button.dataset.accent === accent
            );

        }
    );


    localStorage.setItem(
        "avtarAccent",
        accent
    );

}


function loadTheme() {

    const savedTheme =
        localStorage.getItem(
            "avtarTheme"
        );


    const savedAccent =
        localStorage.getItem(
            "avtarAccent"
        );


    changeTheme(
        savedTheme || "midnight"
    );


    changeAccent(
        savedAccent || "purple"
    );

}


/* =========================================================
   LOGOUT
========================================================= */

function setupLogout() {

    logoutBtn.addEventListener(
        "click",
        logout
    );

}


function logout() {

    const confirmed =
        window.confirm(
            "Are you sure you want to logout?"
        );


    if (!confirmed) {

        return;

    }


    localStorage.removeItem(
        "avtarUser"
    );


    state.user = {

        name: "",
        gender: "",
        role: "student",
        userId: ""

    };


    state.selectedGender =
        "";


    nameInput.value =
        "";

    userIdInput.value =
        "";

    roleInput.value =
        "student";


    genderButtons.forEach(
        button => {

            button.classList.remove(
                "selected"
            );

        }
    );


    messages.innerHTML =
        "";

    fullMessages.innerHTML =
        "";


    dashboardScreen.classList.add(
        "hidden"
    );


    profileScreen.classList.remove(
        "hidden"
    );


    showPage(
        "dashboard"
    );


    addInitialMessage();

}


/* =========================================================
   HELPERS
========================================================= */

function getFirstName() {

    if (
        !state.user.name
    ) {

        return "there";

    }


    return state.user.name
        .split(" ")[0];

}


function capitalize(value) {

    if (!value) {

        return "";

    }


    return (
        value.charAt(0).toUpperCase()
        +
        value.slice(1)
    );

}


function getTime() {

    return new Date()
        .toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );

}


function formatDate(date) {

    return new Date(date)
        .toLocaleString(
            [],
            {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );

}


function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value;


    return div.innerHTML;

}
function setupFullChat() {

    if (!fullSendBtn || !fullMessageInput) {
        return;
    }

    fullSendBtn.addEventListener(
        "click",
        () => {
            sendChatMessage(
                fullMessageInput,
                fullMessages
            );
        }
    );

    if (fullMicBtn) {
        fullMicBtn.addEventListener(
            "click",
            () => toggleVoice(fullMessageInput, fullMessages)
        );
    }

    fullMessageInput.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {

                event.preventDefault();

                sendChatMessage(
                    fullMessageInput,
                    fullMessages
                );
            }
        }
    );
}


function getConversationKey() {

    const name = state.user.name
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-");

    const id = state.user.userId
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-");

    return `avtarConversations:${name}:${id}`;

}


function getActiveConversationKey() {

    return `${getConversationKey()}:active`;

}


function loadConversation() {

    const saved = localStorage.getItem(getConversationKey());

    try {

        state.conversations = saved
            ? JSON.parse(saved)
            : [];

    } catch (error) {

        state.conversations = [];

    }

    // Migrate the earlier single-history format into one saved thread.
    if (state.conversations.length === 0) {

        const legacy = localStorage.getItem(
            getConversationKey().replace(
                "avtarConversations",
                "avtarHistory"
            )
        );

        try {

            const legacyMessages = legacy
                ? JSON.parse(legacy)
                : [];

            if (legacyMessages.length > 0) {

                state.conversations = [{
                    id: `chat-${Date.now()}`,
                    title: "Previous conversation",
                    updatedAt: new Date().toISOString(),
                    messages: legacyMessages
                }];

            }

        } catch (error) {

            state.conversations = [];

        }

    }

    if (state.conversations.length === 0) {

        createNewConversation(false);

        return;

    }

    const savedActive = localStorage.getItem(
        getActiveConversationKey()
    );

    const active = state.conversations.find(
        conversation => conversation.id === savedActive
    ) || state.conversations[0];

    state.activeConversationId = active.id;
    state.history = active.messages || [];

    renderConversation();

    if (state.history.length === 0) {

        addInitialMessage();

    }

}


function saveConversation() {

    const active = state.conversations.find(
        conversation => conversation.id === state.activeConversationId
    );

    if (!active) {

        return;

    }

    active.messages = state.history;
    active.updatedAt = new Date().toISOString();

    const firstUserMessage = state.history.find(
        message => message.sender === "user"
    );

    if (firstUserMessage) {

        active.title = firstUserMessage.text
            .trim()
            .slice(0, 48) || "New conversation";

    }

    localStorage.setItem(
        getConversationKey(),
        JSON.stringify(state.conversations)
    );

    localStorage.setItem(
        getActiveConversationKey(),
        state.activeConversationId
    );

}


function createNewConversation(openChat = true) {

    const conversation = {
        id: `chat-${Date.now()}`,
        title: "New conversation",
        updatedAt: new Date().toISOString(),
        messages: []
    };

    state.conversations.unshift(conversation);
    state.activeConversationId = conversation.id;
    state.history = conversation.messages;

    saveConversation();
    renderConversation();
    addInitialMessage();

    if (openChat) {

        showPage("chat");
        fullMessageInput.focus();

    }

}


function openConversation(id) {

    const conversation = state.conversations.find(
        item => item.id === id
    );

    if (!conversation) {

        return;

    }

    state.activeConversationId = conversation.id;
    state.history = conversation.messages || [];

    saveConversation();
    renderConversation();
    showPage("chat");
    fullMessageInput.focus();

}


function setupConversationControls() {

    newChatBtn.addEventListener(
        "click",
        () => createNewConversation()
    );

}


function addSharedMessage(text, sender) {

    const entry = {
        text: text,
        sender: sender,
        time: new Date().toISOString()
    };

    state.history.push(entry);

    saveConversation();

    [messages, fullMessages].forEach(
        container => addMessage(
            entry.text,
            entry.sender,
            container,
            entry.time
        )
    );

}


function renderConversation() {

    messages.innerHTML = "";
    fullMessages.innerHTML = "";

    state.history.forEach(
        entry => {

            [messages, fullMessages].forEach(
                container => addMessage(
                    entry.text,
                    entry.sender,
                    container,
                    entry.time
                )
            );

        }
    );

}


function showSharedTyping() {

    [messages, fullMessages].forEach(
        container => {

            const typing = document.createElement("div");

            typing.className = "message ai typing-indicator";
            typing.innerHTML =
                "AVTAR is thinking <span class='typing-dots'>•••</span>";

            container.appendChild(typing);
            container.scrollTop = container.scrollHeight;

        }
    );

}


function removeSharedTyping() {

    document.querySelectorAll(
        ".typing-indicator"
    ).forEach(
        item => item.remove()
    );

}


function formatMessageTime(timestamp) {

    return new Date(timestamp).toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


function renderHistory() {

    historyList.innerHTML = "";

    if (state.conversations.length === 0) {

        historyList.innerHTML =
            "<p class='empty-history'>No saved conversation for this user yet.</p>";

        return;

    }

    state.conversations.slice().sort(
        (a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)
    ).forEach(
        conversation => {

            const item = document.createElement("div");

            item.className = "history-item";
            item.innerHTML =
                `<strong>${escapeHtml(conversation.title)}</strong>` +
                `<small>${conversation.messages.length} messages - ${formatMessageTime(conversation.updatedAt)}</small>`;

            item.addEventListener(
                "click",
                () => {

                    openConversation(conversation.id);

                }
            );

            historyList.appendChild(item);

        }
    );

}
function speakText(text) {
    if (!text || !state.voiceEnabled) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;

    window.speechSynthesis.speak(utterance);
}

/* =========================================================
   END
========================================================= */
