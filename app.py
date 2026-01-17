import streamlit as st
import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from loaders import load_pdf, load_docx, load_text, load_video
from agents import (
    extract_structure,
    generate_flashcards,
    generate_summary,
    generate_concept_graph
)


# Helper Functions for Displaying Outputs

def safe_load_json(path):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def draw_concept_graph(graph_data):
    G = nx.DiGraph()

    for node in graph_data.get("nodes", []):
        G.add_node(node)

    for edge in graph_data.get("edges", []):
        if len(edge) == 2:
            G.add_edge(edge[0], edge[1])

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        font_size=9,
        edge_color="gray"
    )
    st.pyplot(plt)
    plt.clf()



# Streamlit Page Config

st.set_page_config(
    page_title="Multi-Source Learning Content Generator",
    layout="wide"
)

st.title("Multi-Source Learning Content Generator")
st.write(
    "Upload PDFs, DOCX, transcripts, or videos and automatically generate "
    "structured learning artifacts like flashcards, summaries, and concept graphs."
)

os.makedirs("outputs", exist_ok=True)


# File Upload

uploaded_file = st.file_uploader(
    "Upload a file (PDF, DOCX, TXT transcript, or MP4 video)",
    type=["pdf", "docx", "txt", "mp4"]
)

extracted_text = ""

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    with st.spinner("Extracting text from uploaded file..."):
        try:
            if file_ext == "pdf":
                extracted_text = load_pdf(uploaded_file)
            elif file_ext == "docx":
                extracted_text = load_docx(uploaded_file)
            elif file_ext == "txt":
                extracted_text = load_text(uploaded_file)
            elif file_ext == "mp4":
                extracted_text = load_video(uploaded_file)
        except Exception as e:
            st.error(f"Error while loading file: {e}")

    if extracted_text:
        st.success("Text extraction completed.")


# Preview Extracted Text

if extracted_text:
    with st.expander(" Preview Extracted Text"):
        st.text_area("Extracted Content", extracted_text[:5000], height=300)


# Run AI Agents

if extracted_text and st.button(" Generate Learning Artifacts"):
    with st.spinner("Running AI agents..."):

        structure = extract_structure(extracted_text)
        with open("outputs/structure.json", "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2)

        flashcards = generate_flashcards(extracted_text)
        with open("outputs/flashcards.json", "w", encoding="utf-8") as f:
            json.dump(flashcards, f, indent=2)

        pd.DataFrame(flashcards).to_csv("outputs/flashcards.csv", index=False)

        summary = generate_summary(extracted_text)
        with open("outputs/summary.md", "w", encoding="utf-8") as f:
            f.write(summary)

        concept_graph = generate_concept_graph(extracted_text)
        with open("outputs/concept_graph.json", "w", encoding="utf-8") as f:
            json.dump(concept_graph, f, indent=2)

    st.success("All learning artifacts generated successfully!")


# Display Outputs

if os.path.exists("outputs/summary.md"):
    st.subheader("Generated Summary")
    with open("outputs/summary.md", "r", encoding="utf-8") as f:
        st.markdown(f.read())

cards = safe_load_json("outputs/flashcards.json")
if cards:
    st.subheader("Flashcards (Preview)")
    for i, card in enumerate(cards[:5]):
        with st.expander(f"Card {i+1}: {card.get('topic', 'General')}"):
            st.markdown(f"** Question:** {card['question']}")
            st.markdown(f"** Answer:** {card['answer']}")

graph = safe_load_json("outputs/concept_graph.json")
if graph:
    st.subheader("Concept Graph")
    draw_concept_graph(graph)
    with st.expander("Raw Graph JSON"):
        st.json(graph)


# Download Section

st.subheader(" Download Outputs")

col1, col2, col3 = st.columns(3)

with col1:
    if os.path.exists("outputs/flashcards.json"):
        st.download_button(
            "Download Flashcards (JSON)",
            open("outputs/flashcards.json", "rb"),
            file_name="flashcards.json"
        )

with col2:
    if os.path.exists("outputs/flashcards.csv"):
        st.download_button(
            "Download Flashcards (CSV)",
            open("outputs/flashcards.csv", "rb"),
            file_name="flashcards.csv"
        )

with col3:
    if os.path.exists("outputs/summary.md"):
        st.download_button(
            "Download Summary (Markdown)",
            open("outputs/summary.md", "rb"),
            file_name="summary.md"
        )
