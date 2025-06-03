const observer = new MutationObserver((mutationsList) => {
    const data = mutationsList.map(m => {
      const target = m.target;
      return {
        type: m.type,
        target: target?.tagName,
        attribute: m.attributeName || null,
        oldValue: m.oldValue || null,
        newValue: target?.getAttribute?.(m.attributeName) || null,
        innerText: target?.innerText || null
      };
    });
  
    fetch("http://104.236.203.213:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mutations: data })
    })
    .then(res => res.json())
    .then(result => {
      console.log("LLM Summary:", result.summary);
      console.log("Dark Pattern Verdict:", result.verdict);
    })
    .catch(err => console.error("Request failed:", err));
  });
  
  observer.observe(document.body, {
    attributes: true,
    attributeOldValue: true,
    childList: true,
    subtree: true
  });
  