from flask import Flask, render_template, request, jsonify, session
import os
import sys
from pathlib import Path
from datetime import timedelta

from prompts.prompts import load_prompt, enrich_analyst_prompt
import json
from datetime import timedelta


ANALYST_PROMPT = load_prompt("prompts/prompt.csv", "Prompt_analyst")
WEEKLY_DATA_PATH = "data/mock_retail_data.csv"


from agent.client import get_client
from settings.config_settings import settings

def create_app() -> Flask:
    # Set template folder to project root's templates directory
    templates_path = 'templates'
    app = Flask(__name__, template_folder=str(templates_path))
    app.secret_key = 'your-secret-key-change-in-production'  # Required for sessions
    app.permanent_session_lifetime = timedelta(hours=1)

    # --- ROUTES ---
    @app.route("/")
    def index():
        session.permanent = True
        if 'messages' not in session:
            session['messages'] = []
        return render_template("index.html")

    @app.route("/chat", methods=["POST"])
    def chat():
        user_message = request.json["message"]
        
        # Initialize messages if not present
        if 'messages' not in session:
            session['messages'] = []

        # Add user message to history
        session['messages'].append({"role": "user", "content": user_message})
        
        # Prepare messages for API (system + history)
        analyst_prompt = enrich_analyst_prompt(ANALYST_PROMPT,WEEKLY_DATA_PATH)

        api_messages = [
            {"role": "system", "content": analyst_prompt}
        ]
        api_messages.extend(session['messages'])

        # Call your LLM API with full conversation history
        client = get_client()
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=api_messages,
            response_format={"type": "json_object"}
        )

        reply = response.choices[0].message.content
        reply = json.loads(reply)
        print(reply)

        
        # Debug: always print the structure to see what we're getting
        print("DEBUG: Reply structure:", json.dumps(reply, indent=2, ensure_ascii=False))
        
        #load those 5 stores lat and lng for routing
        
        data = reply.get("Doporučené_obchody_k_návštěvě")
        
        with open("locations_for_tour.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        session['messages'].append({"role": "assistant", "content": json.dumps(reply)})
        
        # Keep only last 20 messages to avoid token limits
        if len(session['messages']) > 20:
            session['messages'] = session['messages'][-20:]
        
        return jsonify({"reply": reply})
    
    @app.route("/clear", methods=["POST"])
    def clear_history():
        session['messages'] = []
        return jsonify({"status": "cleared"})

    return app