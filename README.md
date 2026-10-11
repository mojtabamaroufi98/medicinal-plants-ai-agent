# 🌿 Medicinal Plant AI Agent

An AI-powered mobile application designed to help users explore medicinal plants, learn about their traditional uses, review available scientific evidence, and understand potential safety concerns.

The project combines Artificial Intelligence, a Python-based agent, plant identification capabilities, and a mobile application interface to provide an accessible plant research experience.

## ✨ Features

- **AI-Powered Plant Research:** Explore medicinal plants and receive structured information about their uses.
- **Scientific Information:** Present available evidence and distinguish scientific support from traditional uses.
- **Plant Identification:** Identify plants from images using the PlantNet API.
- **Safety Information:** Highlight potential warnings and precautions associated with medicinal plants.
- **Persian Language Support:** Designed to provide an accessible experience for Persian-speaking users.
- **Mobile Application:** A mobile interface for interacting with the AI agent.
- **API Integration:** Connect the mobile application to a Python-based backend and AI model providers.

## 🛠️ Technologies Used

- **Python** — Agent logic and backend development
- **AI Language Models** — Natural language understanding and plant research
- **OpenAI-Compatible API** — Communication with supported AI model providers
- **PlantNet API** — Image-based plant identification
- **FastAPI** — Backend API development
- **Kotlin** — Android application development
- **Cloudflare Workers** — API routing and integration
- **Render** — Backend deployment
- **Git & GitHub** — Version control and project documentation

## 🏗️ Project Architecture

The application uses a modular architecture that separates the mobile interface, API communication, and AI processing.

```text
Mobile Application (Kotlin)
          |
          v
Cloudflare Worker
          |
          v
Backend API (FastAPI)
          |
          v
Python AI Agent
          |
          v
AI Model Provider

Plant Images
     |
     v
PlantNet API
     |
     v
Plant Identification
```

The exact request flow depends on the selected feature and backend configuration.

## 🔍 How It Works

1. The user submits a question about a medicinal plant or provides a plant image.
2. The mobile application sends the request to the backend.
3. The AI agent processes the request and generates a structured response.
4. For image-based identification, the application can use PlantNet to identify the plant.
5. The response provides relevant plant information, available evidence, and safety warnings.
6. The application displays the result to the user.

## 🛡️ Safety and Limitations

This project is intended for educational and informational purposes only.

- AI-generated information may be incomplete or inaccurate.
- Traditional medicinal use does not necessarily establish clinical effectiveness.
- Plant identification results should be independently verified before use.
- Medicinal plants may cause adverse effects or interact with medications.
- The application does not replace professional medical advice, diagnosis, or treatment.

**Never use an AI-generated plant identification or recommendation as the sole basis for consuming a medicinal plant.**

## 🚀 Project Goals

This project was developed to explore the practical application of AI agents, API integration, backend development, and Android application development.

It also serves as a foundation for future improvements, including more reliable scientific references, improved response speed, enhanced user experience, and additional plant research capabilities.

## 🔮 Future Improvements

- Integration of more reliable scientific sources
- Improved AI response speed and accuracy
- Enhanced plant identification and verification
- Expanded medicinal plant database
- Improved user interface and accessibility
- Better error handling and request management
- Automated testing and deployment

## 👨‍💻 Developer

Developed as an educational project focused on Artificial Intelligence, Python development, and mobile application engineering.

## 📄 Disclaimer

This application is not a medical device and does not provide professional medical advice. Information about medicinal plants should be verified using reliable scientific sources and qualified healthcare professionals.

---

⭐ If you find this project interesting, consider starring the repository.
