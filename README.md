<img src="https://github.com/AdicOnGit/Line-Privacy-Bot/assets/137413419/f463c43c-a42b-457c-b91d-e0b8fe75df09" width="400" alt="Privacy-Focused Messaging Bot Logo">


# Line-Privacy-Bot

This FastAPI application leverages the LINE Messaging API to offer a unique privacy-focused messaging solution. Designed to act as an intermediary, the bot allows users to send messages to specified groups without revealing their identity, maintaining privacy and anonymity.

## Core Features

- **Privacy-Centric Messaging**: Messages are forwarded through the bot, ensuring that the original sender's identity remains anonymous to other group members.
- **Secure User Authentication**: Implements a robust authentication system to verify users before they can send messages through the bot.
- **Group Message Forwarding**: Authenticated users can send messages to predefined groups without direct interaction, preserving their privacy.
- **Optional Docker Support**: For those preferring containerization, Docker can be used to deploy the application.

## Prerequisites

Ensure you have the following before you start:

- Python 3.11 or later.
- A LINE Messaging API account with an Access Token and Channel Secret.
- `ngrok` for exposing the local development server.

## Setup and Installation

### Getting Started

Clone the repository and set up your environment:

```bash
git clone https://github.com/AdicOnGit/Line-Privacy-Bot.git
cd Line-Privacy-Bot
```

### Environment Setup

Create a `.env` file in the root of your project with the following variables:

```
ACCESS_TOKEN=your_line_access_token
CHANNEL_SECRET=your_line_channel_secret
PASSWORD=your_defined_password_for_user_authentication
```

### Running the Application Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 9999
```

Use `ngrok` to expose the server:

```bash
ngrok http 9999
```

### Optional: Docker Deployment

Build and run the Docker container if you prefer a containerized setup:

```bash
docker build -t your-project-name .
docker run -d -p 9999:9999 your-project-name
```

Expose the Dockerized application with `ngrok` as needed:

```bash
ngrok http 9999
```

## How It Works

- **User Authentication**: Start by sending a "knock knock open the door" message to initiate the authentication process with a predefined password.
- **Privacy-First Messaging**: Once authenticated, any message you send to the bot will be forwarded anonymously to the specified groups. Group members see messages coming from the bot, not the original sender, ensuring your privacy.

### Managing Groups

To control where messages are forwarded, manage group IDs in the `group_id.txt` file. Add or remove IDs as needed.

## Contributing

Contributions to enhance privacy features or overall functionality are welcome. Please open an issue to discuss proposed changes.

## License

This project is under the [MIT License](https://choosealicense.com/licenses/mit/).
