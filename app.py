import gradio as gr
from rag_service import RagService

# init
rag_service = RagService()
# rag_service = None

# Mock user list and group assignment
user_list = {
    "kid123": "Kindergarten",
    "p1_456": "Primary 1-3",
    "p4_789": "Primary 4-6",
}

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

# Create a conversation log
conversation_logs = {}


def login(user_id):
    """Handle user login."""
    if user_id in user_list:
        group = user_list[user_id]
        if user_id not in conversation_logs:
            conversation_logs[user_id] = []  # Initialize user log
        return f"Login successful! You are in group: {group}", group
    else:
        return "Login failed: User ID not found.", None


def ask_question(user_id, group, question):
    """Handle questions and return answers."""
    if not group or user_id not in user_list:
        return "Please log in first.", None

    # Retrieve answer based on question and user group
    # answer = question_database.get(question, {}).get(
    #     group, "Sorry, I couldn't find an answer to your question."
    # )
    # answer = rag_service.rag(group, question)

    # # Save to log
    # if user_id in conversation_logs:
    #     conversation_logs[user_id].append({"question": question, "answer": answer})

    # # Format the log for display
    # formatted_log = "\n".join(
    #     [f"Q: {entry['question']} -> A: {entry['answer']}" for entry in conversation_logs[user_id]]
    # )

    # return answer, formatted_log

    response = ""
    for response in rag_service.rag(group, question):
        yield response, " "

    # Save to log
    if user_id in conversation_logs:
        conversation_logs[user_id].append({"question": question, "answer": response})

    # Format the log for display
    formatted_log = "\n".join(
        [f"Q: {entry['question']} -> A: {entry['answer']}" for entry in conversation_logs[user_id]]
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
                    placeholder="e.g., How do birds fly?",
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

            # liwe = gr.Interface(
            #     fn=(lambda question: ask_question(user_id_input, group_output, question)),
            #     inputs=[
            #         gr.Textbox(
            #             label="What's Your Question?",
            #             placeholder="e.g., How do birds fly?",
            #             lines=2,
            #             elem_classes="gr-textbox"
            #         )
            #     ],
            #     outputs=[
            #         gr.Textbox(
            #             label="✨ Answer ✨",
            #             interactive=False,
            #             value="Your answer will appear here like magic!",
            #             lines=3,
            #             elem_classes="gr-textbox"
            #         ),
            #         gr.Textbox(
            #             label="📜 Your Conversation Log 📜",
            #             interactive=False,
            #             lines=5,
            #             value="Your questions and answers will appear here as you explore!",
            #             elem_classes="gr-textbox"
            #         )
            #     ],
            #     # live=True,
            #     flagging_mode="never",
            #     submit_btn=gr.Button("🔮 Submit Question", elem_classes="gr-button"),
            #     clear_btn=None,
                
            # )

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