import streamlit as st
import os
from groq import Groq

# Streamlit page configuration
st.set_page_config(layout="wide")

# Supported models
SUPPORTED_MODELS = {
    "Llama 3.2 1B (Preview)": "llama-3.2-1b-preview",
    "Llama 3 70B": "llama3-70b-8192",
    "Llama 3 8B": "llama3-8b-8192",
    "Llama 3.1 70B": "llama-3.1-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
    "LLaVA 1.5 7B": "llava-v1.5-7b-4096-preview",
    "Llama 3.2 3B (Preview)": "llama-3.2-3b-preview",
    "Llama 3.2 11B Vision (Preview)": "llama-3.2-11b-vision-preview"
}

MAX_TOKENS = 1000

# Initialize Groq client with API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in environment variables. Please set it and restart the app.")
    st.stop()

client = Groq(api_key=groq_api_key)
st.image("p1.png", width=300)
st.sidebar.image("p2.png", width=200)

def main():
    st.title("Marketing tool App")
    
    # Sidebar settings
    st.sidebar.header("Configuration")
    model = st.sidebar.selectbox("Select LLM Model", list(SUPPORTED_MODELS.keys()))
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
    output_size = st.sidebar.selectbox(
        "Select Output Size",
        ["1-3 word sentences", "2-5 word sentences", "3-7 word sentences", "5-9 word sentences", "6-11 word sentences"]
    )
    bullet_points = st.sidebar.checkbox("Output as Bullet Points", value=True)
    humanize_text = st.sidebar.checkbox("Humanize Text")
    display_final_answer = st.sidebar.checkbox("Display Process", value=True)
    reduce_words = st.sidebar.checkbox("Reduce Word Count by 50%")  # New checkbox for reducing word count

    # Clear and reset buttons in the sidebar
    if st.sidebar.button("Clear Input Fields"):
        st.session_state.system_prompt = "Create a revised [text] use 3-5 words concise and focused, Provide the output in short format plus in bullet points or a brief paragraph,  plus  offer 2-3 alternates - suggest areas for improvement. . list final answer in separate area"
        st.session_state.user_query = ""

    # Input fields for system prompt and query
    default_prompt = "Create a revised [text] use 3-5 words concise and focused, Provide the output in short format plus in bullet points or a brief paragraph,  plus  offer 2-3 alternates - suggest areas for improvement. . list final answer in separate area"
    system_prompt = st.text_area("System Prompt", value=st.session_state.get("system_prompt", default_prompt), key="system_prompt")
    user_query = st.text_area("Enter Your Query", value=st.session_state.get("user_query", ""), key="user_query")
    
    if st.button("Submit"):
        with st.spinner("Generating response..."):
            response = query_groq(model, temperature, system_prompt, user_query, output_size, humanize_text, reduce_words)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Detailed Information")
            st.json({
                "Model": model,
                "Temperature": temperature,
                "Output Size": output_size,
                "Bullet Points": bullet_points,
                "Humanize Text": humanize_text,
                "Display Final Answer": display_final_answer,
                "System Prompt": system_prompt,
                "User Query": user_query
            })
            if display_final_answer:
                st.write("### Original Response")
                st.text_area("Original Response", value=response, height=600)
        
        with col2:
            if display_final_answer:
                processed_response = process_response(response, output_size, bullet_points, humanize_text, reduce_words)
                additional_text = "Please review the response carefully before proceeding."
                st.write("### Processed Response with Review")
                st.text_area(response, value=processed_response + "\n" + additional_text, height=200)
            else:
                st.write("### Output Response")
                st.text(response)
        
def query_groq(model, temperature, system_prompt, user_query, output_size, humanize_text, reduce_words):
    try:
        completion = client.chat.completions.create(
            model=SUPPORTED_MODELS[model],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=temperature,
            max_tokens=MAX_TOKENS
        )
        if not completion.choices:
            return "Error: No choices in the completion response."
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def process_response(text, output_size, bullet_points, humanize_text, reduce_words):
    if reduce_words:
        # Reduce word count by 50%
        words = text.split()
        text = " ".join(words[:len(words)//2])
    
    if output_size == "1-3 word sentences":
        text = reduce_to_sentences(text, 1, 3)
    elif output_size == "2-5 word sentences":
        text = reduce_to_sentences(text, 2, 5)
    elif output_size == "3-7 word sentences":
        text = reduce_to_sentences(text, 3, 7)
    elif output_size == "5-9 word sentences":
        text = reduce_to_sentences(text, 5, 9)
    elif output_size == "6-11 word sentences":
        text = reduce_to_sentences(text, 6, 11)
    
    if bullet_points:
        text = reduce_to_bullet_points(text, 1, 11)
    
    if humanize_text:
        text = humanize(text)
    
    return text

def reduce_to_bullet_points(text, min_words, max_words):
    sentences = text.split('.')
    bullet_points = []
    for sentence in sentences:
        words = sentence.strip().split()
        if min_words <= len(words) <= max_words:
            bullet_points.append(f"- {' '.join(words)}")
    return '\n'.join(bullet_points)

def reduce_to_sentences(text, min_words, max_words):
    sentences = text.split('.')
    filtered_sentences = []
    for sentence in sentences:
        words = sentence.strip().split()
        if min_words <= len(words) <= max_words:
            filtered_sentences.append(sentence.strip())
    return ' '.join(filtered_sentences)

def humanize(text):
    # This can be replaced with a more sophisticated humanization logic as needed
    return text.replace(". ", ". Let's consider this further. ")

st.sidebar.info("build by dw")

if __name__ == "__main__":
    main()
