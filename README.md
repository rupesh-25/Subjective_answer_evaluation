# Subjective Answer Evaluation Project

## Overview

Welcome to the Subjective Answer Evaluation project! Our goal is to leverage the power of AI to automatically evaluate subjective answers in tests, addressing the challenges and limitations posed by traditional manual evaluation.

## Problem Statement

When subjective questions are included in tests taken by a large number of individuals, manual evaluation can be resource-intensive and prone to inconsistencies. Different evaluators may assign varying scores to the same answers, and various factors, including the emotional tone (affect), can influence the evaluation process.

## Our Solution

To overcome these challenges, we're harnessing the capabilities of AI, particularly the Langchain framework. Our approach involves using the GPT-3.5 Turbo model and AI agents to develop a solution for answering questions based solely on the resources provided for exam preparation, such as textbooks.

## Evaluation Process

1. **Answer Generation**: We employ AI agents to generate answers to subjective questions using the provided resources.

2. **Embeddings**: Both the student's answer and the AI-generated answer are converted into embeddings using OpenAI's embeddings model.

3. **Scoring**: We calculate the similarity between these embeddings using cosine similarity. The closer the embeddings, the higher the score assigned to the answer.

## Benefits

By automating the evaluation of subjective answers, we aim to achieve several important goals:

- Consistency in evaluation across all answers.
- Reduction in the manpower required for assessment.
- Enhanced testing with more subjective questions.
- Improved tests that assess an individual's knowledge in a specific domain effectively.

## Getting Started

To get started with our project, please refer to the documentation and code in this repository. We encourage contributions and collaboration to further enhance the capabilities of our system.

Feel free to reach out with any questions or ideas.

**Happy coding!**
