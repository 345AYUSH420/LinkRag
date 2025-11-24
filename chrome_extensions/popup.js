(() => {
    let currentController = null;

    const statusEl = document.getElementById("status");
    const errorEl = document.getElementById("error");
    const answerBox = document.getElementById("answer");
    const questionEl = document.getElementById("question");

    function showStatus(text) {
        statusEl.hidden = false;
        statusEl.textContent = text;
    }

    function hideStatus() {
        statusEl.hidden = true;
        statusEl.textContent = "";
    }

    function showError(text) {
        errorEl.hidden = false;
        errorEl.textContent = text;
    }

    function hideError() {
        errorEl.hidden = true;
        errorEl.textContent = "";
    }

    let currentUrl = null;

    async function saveState() {
        try {
            const state = {
                question: questionEl.value || "",
                answer: answerBox.innerText || ""
            };

            if (!currentUrl) {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                currentUrl = tab?.url;
            }

            if (!currentUrl) {
                chrome.storage.local.set({ linkrag_popup_state: state });
                return;
            }

            chrome.storage.local.get(['linkrag_popup_states'], (res) => {
                const all = res.linkrag_popup_states || {};
                all[currentUrl] = state;
                chrome.storage.local.set({ linkrag_popup_states: all });
            });
        } catch (e) {
            console.warn('Failed to save state', e);
        }
    }

    function restoreState() {
        try {
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                const tab = tabs && tabs[0];
                currentUrl = tab?.url;

                if (!currentUrl) {
                    chrome.storage.local.get(['linkrag_popup_state'], (res) => {
                        const state = res.linkrag_popup_state || {};
                        if (state.question) questionEl.value = state.question;
                        if (state.answer) answerBox.innerText = state.answer;
                    });
                    return;
                }

                chrome.storage.local.get(['linkrag_popup_states'], (res) => {
                    const all = res.linkrag_popup_states || {};
                    const state = all[currentUrl] || {};
                    if (state.question) questionEl.value = state.question;
                    if (state.answer) answerBox.innerText = state.answer;
                });
            });
        } catch (e) {
            console.warn('Failed to restore state', e);
        }
    }

    questionEl.addEventListener('input', () => {
        saveState();
    });

    document.getElementById("askBtn").addEventListener("click", async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = tab?.url;
        const question = document.getElementById("question").value;

        answerBox.innerText = "";
        hideError();

        if (currentController) {
            try { currentController.abort(); } catch (e) {}
            currentController = null;
        }

        const controller = new AbortController();
        currentController = controller;

        let dots = 0;
        showStatus("Loading");
        const dotInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            statusEl.textContent = 'Loading' + '.'.repeat(dots);
        }, 400);

        try {
            const response = await fetch("http://localhost:8000/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url, question }),
                signal: controller.signal
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || `Server returned ${response.status}`);
            }

            if (!response.body) {
                throw new Error("No response body received from server.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let firstChunk = true;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                if (firstChunk) {
                    firstChunk = false;
                    hideStatus();
                }
                answerBox.innerText += chunk;
                saveState();
            }

            hideStatus();
            saveState();
        } catch (err) {
            if (err.name === 'AbortError') {
                showStatus('Cancelled');
            } else {
                console.error(err);
                showError(String(err));
                hideStatus();
            }
            } finally {
            clearInterval(dotInterval);
            currentController = null;
        }
    });
      restoreState();
})();
