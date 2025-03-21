import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    # Open the PDF file in binary mode
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        # Iterate through all the pages and extract text
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

if __name__ == '__main__':
    pdf_file_path = "./Resumes/Keshav Resume.pdf"
    extracted_text = extract_text_from_pdf(pdf_file_path)
    print(extracted_text)
