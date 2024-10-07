import streamlit as st
import os
from groq import Groq
# Streamlit page configuration
st.set_page_config(layout="wide")

# Apply custom CSS for a dark theme

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
    "Llama 3.2 1B (Preview)": "llama-3.2-1b-preview",
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
st.image("p1.png", width=200)
st.sidebar.image("p2.png", width=200)
def main():
    st.title("Marketing tool App")
    
    # Sidebar settings
    st.sidebar.header("Configuration")
    model = st.sidebar.selectbox("Select LLM Model", list(SUPPORTED_MODELS.keys()))
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
    output_size = st.sidebar.selectbox(
        "Select Output Size",
        ["Bullet points 5-9 words", "3-7 word sentences", "6-11 word sentences"]
    )
    humanize_text = st.sidebar.checkbox("Humanize Text")
    
    # Input fields for system prompt and query
    default_prompt = "Create a revised [text] concise and focused, Provide the output in bullet points or a brief paragraph, offer 2-3 alternates - suggest areas for improvement. . list final answer in  separate area"
    system_prompt = st.text_area("System Prompt", value=default_prompt)
    user_query = st.text_area("Enter Your Query")
    
    if st.button("Submit"):
        with st.spinner("Generating response..."):
            response = query_groq(model, temperature, system_prompt, user_query, output_size, humanize_text)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Detailed Information")
            st.json({
                "Model": model,
                "Temperature": temperature,
                "Output Size": output_size,
                "Humanize Text": humanize_text,
                "System Prompt": system_prompt,
                "User Query": user_query
            })
        
        with col2:
            st.write("### Output Response")
            st.text(response)
        
        st.write("### Processed Response")
        if response.startswith("Error:"):
            st.error(response)
        else:
            processed_response = process_response(response, output_size, humanize_text)
            st.write("**Generated Response:**")
            st.text_area(response, value=processed_response, height=200, disabled=True)

def query_groq(model, temperature, system_prompt, user_query, output_size, humanize_text):
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

def process_response(text, output_size, humanize_text):
    if output_size == "Bullet points 5-9 words":
        text = reduce_to_bullet_points(text, 5, 9)
    elif output_size == "3-7 word sentences":
        text = reduce_to_sentences(text, 3, 7)
    elif output_size == "6-11 word sentences":
        text = reduce_to_sentences(text, 6, 11)
    
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
    # TODO: Implement a more sophisticated humanization function
    return text.replace(". ", ". Let's consider this further. ")
st.info("build by dw")
if __name__ == "__main__":
    main()
