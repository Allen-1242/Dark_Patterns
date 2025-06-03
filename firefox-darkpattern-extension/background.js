chrome.browserAction.onClicked.addListener(function(tab) {
    fetch("http://104.236.203.213:8000/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url })
    })
    .then(response => response.json())
    .then(data => console.log("Scan result:", data))
    .catch(error => console.error("Error:", error));
  });
  