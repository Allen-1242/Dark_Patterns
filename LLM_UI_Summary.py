import ollama

def summarize_ui_behavior(mutation_log_lines):
    prompt = """
    
You are a system that summarizes UI behavior based on DOM mutation logs. You must only describe events that are explicitly supported by the mutation data.

Below is a sequence of DOM mutations. Each entry corresponds to a change in the web page's structure or attributes (e.g., class changes, visibility toggles, added text, or modal behavior).

You must output the following:
1. A bullet-point summary of what visibly changed on the page, in order.
2. If the mutation implies user action (e.g., button class changes to show loading), describe it without assuming user intent or follow-up behavior.
3. Do not infer modal closings, additional modals, user typing, or form submissions unless there is direct DOM evidence.
4. If a `hidden` attribute is added, that element is invisible.
5. If `aria-hidden` changes from `true` to `false`, that element becomes visible.
6. If visible text includes things like prices or reviews, state that these were present.
7. Do not use vague terms like “likely” or “may have.” Only describe what changed.

Example Output:
- Button with text "Quick add" changed class to indicate a loading state.
- A disclaimer div was inserted but marked as hidden.
- A modal became visible containing a subscription offer and product details.
- The button class reverted to its original state.

""" + "\n".join(mutation_log_lines)

    response = ollama.chat(
        model='deepseek-r1:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    return response['message']['content']


#Finalizing the summary:
with open("llm_ready_log.txt", "r") as f:
    mutation_lines = [line.strip() for line in f if line.strip()]

# Save summary to file
summary = summarize_ui_behavior(mutation_lines)

with open("summary_output.txt", "w") as f:
    f.write(summary)

print("Summary from DeepSeek R1:\n")
print(summary)