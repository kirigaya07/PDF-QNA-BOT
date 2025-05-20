from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
import google.generativeai as genai # type: ignore
import os
from dotenv import load_dotenv # type: ignore

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
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_answer(self, text: str, question: str) -> str:
        """
        Get an answer to a question based on the provided text using Gemini.
        """
        try:
            # Split the input text into chunks if it's too long
            if len(text) > 30000:  # Gemini has a context length limit
                chunks = self.text_splitter.split_text(text)
                text = "\n".join(chunks[:5])  # Use first 5 chunks to stay within limits

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
            
    def generate_questions(self, text: str) -> list:
        """
        Generate relevant questions based on the document content.
        """
        try:
            # Split the input text into chunks if it's too long
            if len(text) > 30000:  # Gemini has a context length limit
                chunks = self.text_splitter.split_text(text)
                text = "\n".join(chunks[:5])  # Use first 5 chunks to generate questions
            
            # Create the prompt
            prompt = f"""Analyze the following document text and generate 5-7 well-formatted, relevant questions that could be asked about this content.
            
            Focus on creating questions that:
            1. Cover key information in the document
            2. Are clear and specific
            3. Range from simple factual questions to more complex analytical questions
            4. Would be useful for someone trying to understand the document
            
            Document Text:
            {text}
            
            Output only the list of questions, one per line, with no additional text or numbering."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract and format questions
            questions_text = response.text.strip()
            questions_list = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            # Return 5-7 questions or fewer if that's all that was generated
            return questions_list[:7]
            
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")
