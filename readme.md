# SEC 10-K Financial Analysis

## Overview

This project utilizes Retrieval Augmented Generation (RAG) with Claude-Sonnet to analyze the SEC 10-K filings for a given company. It generates a risk heat map along with a brief explanation of the risks, providing a clear and concise visualization of the potential risks the company is facing. The risk heat map can help readers understand the company's risk landscape and potentially develop risk management strategies for the most significant issues.

## Features

- Download and process SEC 10-K filings for a given company
- Clean and preprocess the unstructured filing data
- Implement RAG (Retrieval Augmented Generation) to leverage the context from the filings
- Generate a risk heat map visualizing the potential risks and their impact/likelihood
- Provide a brief explanation of the identified risks

## Backend Tech Stack

The backend stack utilizes RAG to provide the model with the context of the SEC filings, enabling it to answer questions without requiring a lengthy and expensive fine-tuning process.

1. **Data Retrieval and Preprocessing**:
   - `sec_edgar_downloader`: Download the SEC 10-K filings for the specified company.
   - `Unstructured`, `BeautifulSoup`, and `language_tool_python`: Clean the unstructured filing data, handle text formatting, and correct grammatical errors.

2. **RAG Implementation**:
   - `LlamaIndex`: Connect the cleaned filing data to the Claude-Sonnet language model.
   - `ChromaDB`: Store and retrieve vector embeddings for repeated use.
   - `Claude-Sonnet`: The language model used for generating insights and explanations based on the filing data.

3. **Output Generation**:
   - `matplotlib`: Generate the risk heat map visualization based on the identified risks.

4. **API and Caching**:
   - `FastAPI`: Expose the backend functionality as an API.
   - `MongoDB`: Cache the language model results for repeated requests involving the same company, improving performance.

## Frontend Tech Stack

The frontend stack is built using modern web technologies:

- `React` with `Vite`: A powerful and efficient web framework for building user interfaces.
- `Tailwind` and `shadcn/ui`: Styling libraries providing utility classes and UI primitives for creating modern and responsive designs.
- `Axios` and `Tanstack-query`: Libraries for handling API requests and managing asynchronous state in the application.

## Demo

[Demo Video Link](https://drive.google.com/file/d/1CsoilInO_g1L3pRU0S8Ir-2O2eXC-fG6/view?usp=sharing)
