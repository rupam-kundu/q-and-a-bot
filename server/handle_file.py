import csv
import os
from PyPDF2 import PdfReader
import io
import re
import time
from numpy import array, average
from dotenv import load_dotenv
import openai
import tiktoken

def extract_text_from_file(pdf_file_name):
    # Get the path of the directory where the script is saved
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full file path of the PDF file
    pdf_file_path = os.path.join(script_dir, pdf_file_name)
    
    # Return the text content of a file
    with open(pdf_file_path, "rb") as f:
        reader = PdfReader(f)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
    return extracted_text

def chunks(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    # Yield successive n-sized chunks from text
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j

def get_embeddings(text_array, engine):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # openai.api_key = os.environ["OPENAI_API_KEY"]
    # Parameters for exponential backoff
    max_retries = 5 # Maximum number of retries
    base_delay = 1 # Base delay in seconds
    factor = 2 # Factor to multiply the delay by after each retry
    while True:
        try:
            return openai.Engine(id=engine).embeddings(input=text_array)["data"]
        except Exception as e:
            if max_retries > 0:
                print(f"Request failed. Retrying in {base_delay} seconds.")
                time.sleep(base_delay)
                max_retries -= 1
                base_delay *= factor
            else:
                raise e
            
# Compute the column-wise average of a list of lists
def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""
    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        list_of_lists_array = array(list_of_lists)
        average_embedding = average(list_of_lists_array, axis=0)
        return average_embedding.tolist()
    
# Create embeddings for a text using a tokenizer and an OpenAI engine
def create_embeddings_for_text(text, tokenizer):
    token_chunks = list(chunks(text, 1000, tokenizer))
    text_chunks = [tokenizer.decode(chunk) for chunk in token_chunks]

    # Split text_chunks into shorter arrays of max length 10
    # text_chunks_arrays = [text_chunks[i:i+100] for i in range(0, len(text_chunks), 100)]
    
    text_chunks_arrays = text_chunks
    # Call get_embeddings for each shorter array and combine the results
    embeddings = []
    for text_chunks_array in text_chunks_arrays:
        embeddings_response = get_embeddings(text_chunks_array, "text-embedding-ada-002")
        embeddings.extend([embedding["embedding"] for embedding in embeddings_response])

    text_embeddings = list(zip(text_chunks, embeddings))

    average_embedding = get_col_average_from_list_of_lists(embeddings)

    return (text_embeddings, average_embedding)
            
# Handle a file string by creating embeddings and upserting them to Pinecone
def handle_file_string(filename, file_body_string, tokenizer):
    
    clean_file_body_string = file_body_string
    
    text_to_embed = clean_file_body_string

    # Create embeddings for the text
    try:
        text_embeddings, average_embedding = create_embeddings_for_text(
            text_to_embed, tokenizer)
        
        # Write the embeddings to a CSV file
        with open("embeddings.csv", mode="w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['index', 'text', 'embedding'])
            for i, (text_chunk, embedding) in enumerate(text_embeddings):
                writer.writerow([i, text_chunk, embedding])
        print("Embeddings written to embeddings.csv.")
        
    except Exception as e:
        print(
            "[handle_file_string] Error creating embedding: {}".format(e))
        raise e
    
# Handle a file by extracting its text, creating embeddings, and upserting them to Pinecone
def handle_file(filename):
    # tokenizer = tiktoken.get_encoding("gpt2")
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    # Extract text from the file
    extracted_text = extract_text_from_file(filename)
    
    # Handle the extracted text as a string
    return handle_file_string(filename, extracted_text, tokenizer)

# Handle the PDF file   
handle_file("PIIS0092867413006454.pdf")
