## AI Assistants

This document explains how to create and configure AI Assistants within the Practicus AI platform. It includes step-by-step instructions for adding new AI Assistants, configuring their connection to underlying APIs or models, and adjusting important inference-related settings (e.g., temperature, max tokens).  

---

## Overview

An AI Assistant is a configurable endpoint that allows you to integrate different underlying model providers or APIs (such as Practicus AI Model API, Practicus AI App API, or external APIs like OpenAI). By defining an AI Assistant, you centralize the settings and authentication tokens necessary for users to interact with your models or AI services.

---

## Accessing AI Assistants

1. In the left-hand navigation menu, expand the **Generative AI** section.  
2. Click **AI Assistants** to open the list of existing AI Assistants.  
3. From the AI Assistants overview page, you can view, edit, or create new assistants.  


- **Key**: Unique identifier for each AI Assistant.  
- **Name**: Human-readable name.  
- **API interface**: Indicates the selected connection method (e.g., OpenAI, Auto).  
- **Model API**, **App API**, **Custom API**: The configured back-end for the AI.  
- **Sort order**: The position in which the assistant is displayed in the user interface.

    ![](img\ai_01.png)

---

## Adding a New AI Assistant

### Step 1: Open the "Add AI Assistant" Form

- Click the **+ (Add)** button in the top-right corner (or select **Add AI Assistant** if available).  

You will be redirected to the **Add AI Assistant** page.  


### Step 2: Fill Out Basic Information

- **Key** *(Required)*:  
  - A unique identifier using lowercase letters, digits, or dashes (e.g., `assistant-1`).  
- **Name** *(Recommended)*:  
  - A short, descriptive name for the AI Assistant.  
  - Useful if multiple models or endpoints are being used.  
- **Description** *(Optional)*:  
  - A short summary describing the assistant’s behavior, capabilities, or specialized domain.

![](img\ai_02.png)

### Step 3: Select the Interface and APIs

- **API interface**:  
  - Determines which type of endpoint this AI Assistant will connect to.  
  - Options might include `Auto` (system decides automatically), `OpenAI`, or other integrated providers.  
- **Model API**:  
  - If you want to connect to a Practicus AI Model API, select it here.  
  - If set, the assistant will use user permissions for that specific model.  
- **App API**:  
  - If you want to connect to a Practicus AI App API, select it here.  
  - If set, the assistant will use user permissions for that specific app.  
- **Custom API**:  
  - Use this field to set a base URL for a non-Practicus API endpoint (e.g., OpenAI’s `https://api.openai.com/v1`).  

![](img\ai_03.png)

### Step 4: Configure Access Tokens and Parameters

- **Custom token**:  
  - Specify a custom token if the external API requires one (e.g., an API key).  
  - If left blank, a token will be generated automatically for Practicus AI models or apps.  
  - For external APIs (like OpenAI), you must provide your own token.  
- **Model name**:  
  - Indicates which model to use if the endpoint can serve multiple models (e.g., `llama-3-8b`).  
  - Leave blank to use a default or single model.  
- **Temperature**:  
  - Controls the randomness of AI-generated text.  
  - Higher values produce more varied output; lower values produce more deterministic output.  
- **Max tokens**:  
  - Sets a limit on the number of tokens in the generated response.  
- **Custom config**:  
  - An optional JSON field where you can supply additional configuration parameters, including required headers for certain APIs (e.g., `OpenAI-Organization`).  

![](img\ai_04.png)

### Step 5: Sort Order

- **Sort order** *(Required)*:  
  - Determines the display order of AI Assistants in the user interface.  
  - Higher numbers appear later in the list.

![](img\ai_05.png)

### Step 6: Save Your New AI Assistant

At the bottom of the form, you have several options:  
- **Save and add another**: Save the current Assistant and start configuring a new one immediately.  
- **Save and continue editing**: Save the current Assistant but remain on the same page for further modifications.  
- **Save**: Save the current Assistant and return to the AI Assistants list.

---

## Managing Existing AI Assistants

1. From the **AI Assistants** list, select the checkbox next to an Assistant or click its name to view details.  
2. Use **Select action** (if multiple are selected) or the edit icon to make changes to the selected Assistant.  
3. Update the fields (e.g., API interface, tokens, model parameters) as needed.  
4. Click **Save** to confirm any changes.

---


[< Previous](enterprise-sso.md) | [Next >](mfa.md)