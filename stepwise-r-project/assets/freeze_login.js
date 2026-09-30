(() => {
  const message = document.getElementById("message");
  const key = new URLSearchParams(location.hash.slice(1)).get("key");
  if (!key) {
    message.textContent = "请使用 Codex 返回的完整工作台链接。";
    return;
  }
  history.replaceState(null, "", "/");
  fetch("/api/login", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  }).then(response => {
    if (!response.ok) throw new Error("链接已失效");
    location.replace("/");
  }).catch(error => { message.textContent = error.message; });
})();
