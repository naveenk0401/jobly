from google_auth_oauthlib.flow import InstalledAppFlow
import os

def main():
    # Make sure you have credentials.json in the same folder
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json not found in the current directory.")
        print("Please download it from Google Cloud Console (APIs & Services -> Credentials).")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    creds = flow.run_local_server(port=0)
    print("\n✅ Authentication Successful!")
    print("REFRESH_TOKEN:", creds.refresh_token)
    print("\nCopy this REFRESH_TOKEN to your backend/.env file.")

if __name__ == "__main__":
    main()
