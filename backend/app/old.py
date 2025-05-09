from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class QAEngine:
    def __init__(self):
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Configure Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    def get_answer(self, text: str, question: str) -> str:
        """
        Get an answer to a question based on the provided text using Gemini.
        """
        try:
            # Split the input text into chunks if it's too long
            if len(text) > 30000:  # Gemini has a context length limit
                chunks = self.text_splitter.split_text(text)
                text = "\n".join(chunks[:3])  # Use first 3 chunks to stay within limits

            # Create the prompt
            prompt = f"""Based on the following text, please answer the question. 
            If the answer is not in the text, say "I cannot find the answer in the provided text."

            Text:
            {text}

            Question: {question}

            Please provide a clear and concise answer:"""

            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract and return the answer
            answer = response.text.strip()
            return answer

        except Exception as e:
            raise Exception(f"Error getting answer: {str(e)}")
