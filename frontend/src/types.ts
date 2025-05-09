export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  upload_date: string;
  file_path: string;
  text_content: string;
}

export interface Question {
  document_id: number;
  question: string;
}

export interface Answer {
  answer: string;
}
