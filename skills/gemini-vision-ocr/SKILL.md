---
name: gemini-vision-ocr
description: Expert image transcription and visual data extraction using Gemini 3 Flash.
author: Gemini
version: 1.0.0
tools:
  - name: transcribe_image
    description: Extracts text, tables, and structured data from an image file path or URL.
    parameters:
      path: string (required) - Local path or URL to the image.
      format: string (optional) - Preferred output format (markdown, json, plain_text).
---

# Gemini Vision OCR Skill

This skill allows the OpenClaw agent to "see" and transcribe images with high fidelity using the gemini-3-flash model.

## Instructions

When a user provides an image or a path to an image, trigger the transcribe_image tool.

### System Prompt for Gemini 3 Flash:

"You are a high-precision OCR engine. Your task is to transcribe the provided image into {format}.
- Maintain the original layout and hierarchy of the text.
- If tables are present, render them as clean Markdown tables.
- If handwriting is present, transcribe it with [Handwritten] tags.
- Ignore 'AI slop' or background noise unless it contains relevant data."

## Usage Example

User: "Can you read this screenshot and give me the list in a table?"

Agent: *Calls transcribe_image(path="screenshot.png", format="markdown")*

## Implementation Note

Ensure GEMINI_API_KEY is set in your credentials.

This skill uses gemini-3-flash for maximum accuracy in image transcription.
