#!/usr/bin/env python3
"""
Safari Google FX Flow Automator for macOS
Native AppleScript & DOM Automation tool to control Google FX Flow in Safari.
"""

import subprocess
import json
import sys
import time

def run_safari_js(js_code):
    # Escape quotes for AppleScript
    escaped_js = js_code.replace('\\', '\\\\').replace('"', '\\"')
    cmd = f'osascript -e \'tell application "Safari" to do JavaScript "{escaped_js}" in current tab of window 1\''
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

def click_new_project():
    print("[1/3] Searching for '+ Nuevo proyecto' button in Safari...")
    js = """
    (function() {
        const btns = Array.from(document.querySelectorAll('button, div[role="button"], span, div'));
        const newProjBtn = btns.find(b => b.innerText && b.innerText.includes('Nuevo proyecto'));
        if (newProjBtn) {
            newProjBtn.click();
            return "SUCCESS: Clicked '+ Nuevo proyecto'";
        }
        return "ERROR: '+ Nuevo proyecto' button not found";
    })()
    """
    result = run_safari_js(js)
    print(f"Result: {result}")
    return result

def inspect_canvas_nodes():
    print("[2/3] Inspecting active Flow canvas nodes...")
    js = """
    (function() {
        const nodes = Array.from(document.querySelectorAll('div[class*="node"], div[class*="card"], div[role="region"]'));
        const textareas = Array.from(document.querySelectorAll('textarea, input[type="text"]')).map(t => t.value);
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(b => b.length > 0);
        return JSON.stringify({
            nodes_found: nodes.length,
            textareas: textareas,
            buttons: buttons.slice(0, 15)
        });
    })()
    """
    result = run_safari_js(js)
    print(f"Canvas state: {result}")
    return result

def set_prompt_and_generate(prompt_text):
    print(f"[3/3] Setting prompt: '{prompt_text}' and triggering generation...")
    js = f"""
    (function() {{
        const textareas = Array.from(document.querySelectorAll('textarea'));
        if (textareas.length > 0) {{
            const target = textareas[0];
            target.value = "{prompt_text}";
            target.dispatchEvent(new Event('input', {{ bubbles: true }}));
            target.dispatchEvent(new Event('change', {{ bubbles: true }}));
            
            // Try to find generate button
            const btns = Array.from(document.querySelectorAll('button'));
            const genBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('generar') || b.innerText.toLowerCase().includes('generate') || b.innerText.toLowerCase().includes('run')));
            if (genBtn) {{
                genBtn.click();
                return "SUCCESS: Prompt injected and Generate clicked!";
            }}
            return "SUCCESS: Prompt injected into node textarea.";
        }}
        return "ERROR: No prompt textareas found on canvas.";
    }})()
    """
    result = run_safari_js(js)
    print(f"Result: {result}")
    return result

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "inspect"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "A futuristic cyberpunk city in neon aesthetics, 8k resolution"
    
    if action == "new_project":
        click_new_project()
    elif action == "inspect":
        inspect_canvas_nodes()
    elif action == "generate":
        set_prompt_and_generate(prompt)
    elif action == "full_flow":
        click_new_project()
        time.sleep(2)
        inspect_canvas_nodes()
        time.sleep(1)
        set_prompt_and_generate(prompt)

if __name__ == "__main__":
    main()
