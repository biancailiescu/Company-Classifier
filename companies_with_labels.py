# -*- coding: utf-8 -*-
"""companies_with_labels.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jCE0FoFnWYIshit_w3hL83OD87agAaS6
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

companies = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/Veridion challenge/companies_with_insurance_categories.csv')
insurance_labels = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/Veridion challenge/clusterized_labels.csv')

print(companies["insurance_category"])

print(insurance_labels["label"])

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def assign_labels_with_sbert(companies, insurance_labels, top_n=1):
    assigned_labels = []

    for _, company_row in companies.iterrows():
        category = company_row['insurance_category']
        filtered_labels = insurance_labels[insurance_labels['insurance_category'] == category]

        if filtered_labels.empty:
            assigned_labels.append([])
            continue

        company_text = company_row['processed_description']
        if isinstance(company_text, float):
            company_text = str(company_text)

        label_texts = filtered_labels['label'].fillna("")

        company_embedding = model.encode(company_text, convert_to_tensor=True)
        label_embeddings = model.encode(label_texts.tolist(), convert_to_tensor=True)

        similarities = cosine_similarity(company_embedding.unsqueeze(0).cpu(), label_embeddings.cpu()).flatten()

        top_indices = similarities.argsort()[-top_n:][::-1]
        top_labels = filtered_labels.iloc[top_indices]['label'].tolist()

        assigned_labels.append(top_labels)

    companies['assigned_labels'] = assigned_labels
    return companies

companies_with_multiple_labels = assign_labels_with_sbert(companies, insurance_labels, top_n=1)

companies_with_multiple_labels.to_csv("/content/drive/MyDrive/Colab Notebooks/Veridion challenge/final_dataset.csv", index=False)

companies_with_multiple_labels.rename(columns={'assigned_labels': 'insurance_label'}, inplace=True)

