import gradio as gr
import csv
import os
import sqlite3
from rag_service import RagService

# init
rag_service = RagService()

# Path configurations
USER_CSV_PATH = "data/users.csv"
DB_PATH = "data/conversation_logs.db"

# Ensure directories exist
os.makedirs(os.path.dirname(USER_CSV_PATH), exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def load_users_from_csv():
    """Load user list from CSV file. Create if not exists."""
    user_list = {}
    
    # Create default CSV if it doesn't exist
    if not os.path.exists(USER_CSV_PATH):
        with open(USER_CSV_PATH, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['user_id', 'group'])
            # Add default users
            writer.writerow(['kid123', 'Kindergarten'])
            writer.writerow(['p1_456', 'Primary 1-3'])
            writer.writerow(['p4_789', 'Primary 4-6'])
    
    # Read from CSV
    with open(USER_CSV_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                user_list[row[0]] = row[1]
    
    return user_list

# Initialize database
def init_database():
    """Initialize SQLite database for conversation logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        question TEXT,
        answer TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Load user list and initialize database
user_list = load_users_from_csv()
init_database()

# Mock question database
question_database = {
    "What is the sky?": {
        "Kindergarten": "The sky is the big blue space you see above you!",
        "Primary 1-3": "The sky is the atmosphere we see above, which looks blue due to sunlight scattering.",
        "Primary 4-6": "The sky is the layer of gases surrounding the Earth, appearing blue due to Rayleigh scattering of sunlight.",
    },
    "What are stars?": {
        "Kindergarten": "Stars are twinkling lights in the night sky!",
        "Primary 1-3": "Stars are huge balls of burning gas, far away in space.",
        "Primary 4-6": "Stars are massive celestial bodies made mostly of hydrogen and helium that produce light through nuclear fusion.",
    },
}

def get_user_conversation_logs(user_id):
    """Retrieve conversation logs for a specific user from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, answer FROM conversation_logs WHERE user_id = ? ORDER BY timestamp",
        (user_id,)
    )
    logs = [{"question": q, "answer": a} for q, a in cursor.fetchall()]
    conn.close()
    return logs

def save_conversation(user_id, question, answer):
    """Save conversation to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversation_logs (user_id, question, answer) VALUES (?, ?, ?)",
        (user_id, question, answer)
    )
    conn.commit()
    conn.close()

def login(user_id):
    """Handle user login."""
    if user_id in user_list:
        group = user_list[user_id]
        return f"Login successful! You are in group: {group}", group
    else:
        return "Login failed: User ID not found.", None

def ask_question(user_id, group, question):
    """Handle questions and return answers."""
    if not group or user_id not in user_list:
        return "Please log in first.", None

    response = ""
    for response in rag_service.rag(group, question):
        yield response, " "

    # Save to database
    save_conversation(user_id, question, response)

    # Get logs from database and format for display
    logs = get_user_conversation_logs(user_id)
    formatted_log = "\n".join(
        [f"{index}.Q: {entry['question']} -> A: {entry['answer']}" for index, entry in enumerate(logs)]
    )

    yield response, formatted_log

def main():
    # Gradio interface with custom styling
    with gr.Blocks(theme=gr.themes.Base(), css_paths="static/css/gradio_css.css") as demo:
        # 添加装饰元素
        demo.load(
            fn=None,
            inputs=None,
            outputs=None,
            js=open(r'static/js/gradio_js.js', 'r', encoding='utf-8').read()
        )
    
        gr.Markdown("""
            <h1>🌈 Welcome to the Children's Q&A Platform 🌈</h1>
            <p>Log in with your User ID and ask questions about science, culture, and more!</p>
        """,elem_classes="gr-markdown")

        with gr.Group(elem_classes="gr-blocks"):
            gr.Markdown("<h1>✨ Login to Your Adventure ✨</h1>",elem_classes="gr-markdown")
            with gr.Row(elem_classes="gr-row"):
                user_id_input = gr.Textbox(
                    label="Enter Your User ID",
                    placeholder="e.g., kid123",
                    lines=1,
                    max_lines=1,
                    elem_classes="gr-textbox"
                )
                login_button = gr.Button("🚀 Login", elem_classes="gr-button")
            
            login_output = gr.Textbox(
                label="Login Status",
                interactive=False,
                value="Waiting for your superhero name...",
                elem_classes="gr-textbox"
            )
            group_output = gr.Textbox(
                label="User Group",
                interactive=False,
                value="Your journey begins when you login!",
                elem_classes="gr-textbox"
            )

        with gr.Group(elem_classes="gr-blocks"):
            gr.Markdown("<h1>❓ Ask a Question ❓</h1>",
                    elem_classes="gr-markdown")
            with gr.Row():
                question_input = gr.Textbox(
                    label="What's Your Question?",
                    placeholder="e.g., What is computer?",
                    lines=2,
                    elem_classes="gr-textbox"
                )
                question_button = gr.Button("🔮 Submit Question", elem_classes="gr-button")
            
            answer_output = gr.Textbox(
                label="✨ Answer ✨",
                interactive=False,
                value="Your answer will appear here like magic!",
                lines=3,
                elem_classes="gr-textbox"
            )
            
            log_output = gr.Textbox(
                label="📜 Your Conversation Log 📜",
                interactive=False,
                lines=5,
                value="Your questions and answers will appear here as you explore!",
                elem_classes="gr-textbox"
            )

        # 事件处理
        login_button.click(
            login,
            inputs=[user_id_input],
            outputs=[login_output, group_output]
        )
        
        question_button.click(
            ask_question,
            inputs=[user_id_input, group_output, question_input],
            outputs=[answer_output, log_output]
        )

    # 启动应用
    demo.launch(
        favicon_path="static/favicon/image.png",
        height=800
    )

if __name__ == "__main__":
    main()